from web3 import Web3
import json
import time
from datetime import datetime
import logging
from typing import Dict, Optional
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('copy_trader.log'),
        logging.StreamHandler()
    ]
)

class HyperliquidTrader:
    def __init__(self):
        # Validate environment variables first
        self._validate_environment()
        
        # Initialize Web3 connection to Arbitrum
        arbitrum_rpc = os.getenv('ARBITRUM_RPC_URL')
        if not arbitrum_rpc:
            raise ValueError("ARBITRUM_RPC_URL not found in environment variables")
        
        self.w3 = Web3(Web3.HTTPProvider(arbitrum_rpc))
        
        # Load configuration
        self.config = {
            'private_key': os.getenv('PRIVATE_KEY'),
            'max_position_size': float(os.getenv('MAX_POSITION_SIZE', '0.1')),  # Maximum position size in ETH
            'leverage': float(os.getenv('LEVERAGE', '2.0')),  # Default leverage
            'min_profit_threshold': float(os.getenv('MIN_PROFIT_THRESHOLD', '0.02')),  # 2% minimum profit
            'stop_loss_percentage': float(os.getenv('STOP_LOSS_PERCENTAGE', '0.05')),  # 5% stop loss
        }
        
        # Initialize account
        self.account = self.w3.eth.account.from_key(self.config['private_key'])
        
        # Hyperliquid contract addresses
        self.contracts = {
            'clearinghouse': os.getenv('CLEARINGHOUSE_ADDRESS'),
            'exchange': os.getenv('EXCHANGE_ADDRESS'),
            'usdc': os.getenv('USDC_ADDRESS')
        }
        
        # Load contract ABIs (optional for Discord-only mode)
        self.contracts_loaded = self.load_contracts()
        
        # Initialize trade tracking
        self.active_trades: Dict[str, Dict] = {}
        
    def _validate_environment(self):
        """Validate that all required environment variables are present and valid"""
        required_vars = [
            'ARBITRUM_RPC_URL',
            'PRIVATE_KEY',
            'CLEARINGHOUSE_ADDRESS', 
            'EXCHANGE_ADDRESS',
            'USDC_ADDRESS'
        ]
        
        missing_vars = []
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Validate private key format
        private_key = os.getenv('PRIVATE_KEY')
        if private_key:
            # Remove 0x prefix if present
            if private_key.startswith('0x'):
                private_key = private_key[2:]
            
            # Check if it's valid hex and correct length
            if len(private_key) != 64:
                raise ValueError("Private key must be 64 characters long (32 bytes)")
            
            try:
                int(private_key, 16)
            except ValueError:
                raise ValueError("Private key must be a valid hexadecimal string")
            
            # Update the environment variable with cleaned format
            os.environ['PRIVATE_KEY'] = '0x' + private_key
        
        logging.info("Environment validation passed")
        
    def load_contracts(self):
        """Load contract ABIs and initialize contract instances"""
        try:
            # Check if ABI files exist
            abi_files = [
                'abis/hyperliquid_clearinghouse.json',
                'abis/hyperliquid_exchange.json', 
                'abis/usdc.json'
            ]
            
            missing_files = []
            for file_path in abi_files:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            if missing_files:
                logging.warning(f"Missing ABI files: {', '.join(missing_files)}")
                logging.warning("Bot will run in Discord-only mode (no actual trading)")
                self.clearinghouse = None
                self.exchange = None
                self.usdc = None
                return False
            
            # Load Hyperliquid contract ABIs
            with open('abis/hyperliquid_clearinghouse.json', 'r') as f:
                clearinghouse_abi = json.load(f)
            
            with open('abis/hyperliquid_exchange.json', 'r') as f:
                exchange_abi = json.load(f)
            
            with open('abis/usdc.json', 'r') as f:
                usdc_abi = json.load(f)
            
            # Check if contract addresses are provided
            if not all([self.contracts['clearinghouse'], self.contracts['exchange'], self.contracts['usdc']]):
                logging.warning("Contract addresses not configured. Bot will run in Discord-only mode")
                self.clearinghouse = None
                self.exchange = None
                self.usdc = None
                return False
            
            # Initialize contracts
            self.clearinghouse = self.w3.eth.contract(
                address=self.w3.to_checksum_address(self.contracts['clearinghouse']),
                abi=clearinghouse_abi
            )
            
            self.exchange = self.w3.eth.contract(
                address=self.w3.to_checksum_address(self.contracts['exchange']),
                abi=exchange_abi
            )
            
            self.usdc = self.w3.eth.contract(
                address=self.w3.to_checksum_address(self.contracts['usdc']),
                abi=usdc_abi
            )
            
            logging.info("Contracts loaded successfully - trading enabled")
            return True
                
        except Exception as e:
            logging.error(f"Error loading contracts: {str(e)}")
            logging.warning("Bot will run in Discord-only mode (no actual trading)")
            self.clearinghouse = None
            self.exchange = None
            self.usdc = None
            return False

    def get_market_info(self, symbol: str) -> Dict:
        """Get market information from Hyperliquid API"""
        try:
            response = requests.get(f"https://api.hyperliquid.xyz/info")
            if response.status_code == 200:
                markets = response.json()
                for market in markets:
                    if market['symbol'] == symbol:
                        return market
            return None
        except Exception as e:
            logging.error(f"Error fetching market info: {str(e)}")
            return None

    def get_position_size(self, symbol: str, price: float) -> int:
        """Calculate position size in USDC"""
        try:
            # Get account balance
            balance = self.usdc.functions.balanceOf(self.account.address).call()
            balance_usdc = balance / 1e6  # Convert from 6 decimals
            
            # Calculate position size based on max position size and leverage
            position_size = min(
                balance_usdc * self.config['leverage'],
                self.config['max_position_size'] * price
            )
            
            return int(position_size * 1e6)  # Convert back to 6 decimals
        except Exception as e:
            logging.error(f"Error calculating position size: {str(e)}")
            return 0

    def receive_trade_signal(self, signal_data: Dict):
        """Process incoming trade signals"""
        try:
            # Validate signal data
            required_fields = ['action', 'symbol', 'price']
            if not all(field in signal_data for field in required_fields):
                logging.error("Invalid signal data: missing required fields")
                return False
            
            # Check if contracts are loaded for actual trading
            if not self.contracts_loaded:
                logging.info(f"Signal received: {signal_data['action']} {signal_data['symbol']} @ ${signal_data['price']}")
                logging.warning("Contracts not loaded - signal logged but not executed")
                return True  # Return True so Discord bot shows success for testing
            
            # Update leverage if provided
            if 'leverage' in signal_data:
                self.config['leverage'] = float(signal_data['leverage'])
            
            # Process the trade signal
            if signal_data['action'] == 'BUY':
                return self.execute_buy(signal_data)
            elif signal_data['action'] == 'SELL':
                return self.execute_sell(signal_data)
            else:
                logging.error(f"Invalid action: {signal_data['action']}")
                return False
                
        except Exception as e:
            logging.error(f"Error processing trade signal: {str(e)}")
            return False

    def execute_buy(self, signal_data: Dict) -> bool:
        """Execute a buy order on Hyperliquid"""
        try:
            symbol = signal_data['symbol']
            price = float(signal_data['price'])
            
            # Get market info
            market_info = self.get_market_info(symbol)
            if not market_info:
                logging.error(f"Market info not found for {symbol}")
                return False
            
            # Calculate position size
            position_size = self.get_position_size(symbol, price)
            if position_size == 0:
                logging.error("Invalid position size")
                return False
            
            # Build transaction
            transaction = self.exchange.functions.openPosition(
                market_info['id'],
                position_size,
                int(price * 1e6),  # Convert price to 6 decimals
                self.config['leverage'],
                True  # isLong
            ).build_transaction({
                'from': self.account.address,
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'chainId': 42161  # Arbitrum chain ID
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.config['private_key'])
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt['status'] == 1:
                # Record the trade
                self.active_trades[symbol] = {
                    'entry_price': price,
                    'position_size': position_size,
                    'leverage': self.config['leverage'],
                    'timestamp': datetime.now(),
                    'tx_hash': tx_hash.hex()
                }
                logging.info(f"Buy order executed successfully: {tx_hash.hex()}")
                return True
            else:
                logging.error("Buy order failed")
                return False
                
        except Exception as e:
            logging.error(f"Error executing buy order: {str(e)}")
            return False

    def execute_sell(self, signal_data: Dict) -> bool:
        """Execute a sell order on Hyperliquid"""
        try:
            symbol = signal_data['symbol']
            
            # Check if we have an active position
            if symbol not in self.active_trades:
                logging.error("No active position to sell")
                return False
            
            # Get market info
            market_info = self.get_market_info(symbol)
            if not market_info:
                logging.error(f"Market info not found for {symbol}")
                return False
            
            # Build transaction
            transaction = self.exchange.functions.closePosition(
                market_info['id'],
                self.active_trades[symbol]['position_size'],
                int(float(signal_data['price']) * 1e6)  # Convert price to 6 decimals
            ).build_transaction({
                'from': self.account.address,
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'chainId': 42161  # Arbitrum chain ID
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.config['private_key'])
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt['status'] == 1:
                # Calculate profit/loss
                entry_price = self.active_trades[symbol]['entry_price']
                exit_price = float(signal_data['price'])
                profit_percentage = (exit_price - entry_price) / entry_price * self.config['leverage']
                
                logging.info(f"Sell order executed successfully: {tx_hash.hex()}")
                logging.info(f"Profit/Loss: {profit_percentage:.2%}")
                
                # Remove from active trades
                del self.active_trades[symbol]
                return True
            else:
                logging.error("Sell order failed")
                return False
                
        except Exception as e:
            logging.error(f"Error executing sell order: {str(e)}")
            return False

    def check_positions(self):
        """Check active positions for stop loss or take profit conditions"""
        for symbol, trade in self.active_trades.items():
            try:
                # Get current price from Hyperliquid API
                market_info = self.get_market_info(symbol)
                if not market_info:
                    continue
                    
                current_price = float(market_info['price'])
                
                # Calculate profit/loss
                profit_percentage = (current_price - trade['entry_price']) / trade['entry_price'] * trade['leverage']
                
                # Check stop loss
                if profit_percentage <= -self.config['stop_loss_percentage']:
                    logging.info(f"Stop loss triggered for {symbol}")
                    self.execute_sell({
                        'action': 'SELL',
                        'symbol': symbol,
                        'price': current_price
                    })
                
                # Check take profit
                elif profit_percentage >= self.config['min_profit_threshold']:
                    logging.info(f"Take profit triggered for {symbol}")
                    self.execute_sell({
                        'action': 'SELL',
                        'symbol': symbol,
                        'price': current_price
                    })
                    
            except Exception as e:
                logging.error(f"Error checking position for {symbol}: {str(e)}")

def main():
    # Initialize trader
    trader = HyperliquidTrader()
    
    # Example of processing a trade signal
    sample_signal = {
        'action': 'BUY',
        'symbol': 'BTC',
        'price': '50000.0',
        'leverage': '2.0'
    }
    
    # Process the signal
    trader.receive_trade_signal(sample_signal)
    
    # Start monitoring positions
    while True:
        trader.check_positions()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main() 