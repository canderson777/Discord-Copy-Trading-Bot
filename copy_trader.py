from web3 import Web3
import json
import time
from datetime import datetime
import logging
import re
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

    def _parse_tp_fractions(self, tp_count: int) -> list:
        """Return a list of TP fractions (of original position) to close per TP.
        - Reads TP_FRACTIONS from env if provided (comma or slash separated).
        - Accepts decimals (0.25) or percentages (25, 25%).
        - Falls back to equal fractions across TP count.
        """
        try:
            raw = os.getenv('TP_FRACTIONS')
            if raw:
                # Split on comma, slash, or whitespace
                parts = re.split(r'[\s,\/]+', raw.strip())
                nums = []
                for p in parts:
                    if not p:
                        continue
                    p = p.replace('%', '')
                    val = float(p)
                    if val > 1.0:
                        val = val / 100.0
                    nums.append(val)
                # If counts mismatch, fallback to equal splits
                if len(nums) != tp_count:
                    if tp_count > 0:
                        return [1.0 / float(tp_count)] * tp_count
                    return []
                total = sum(nums)
                if total <= 0:
                    return [1.0 / float(tp_count)] * tp_count if tp_count > 0 else []
                # Normalize to sum to 1.0
                return [n / total for n in nums]
            # Default: equal fractions; for 3 TPs this is ~33% each
            return [1.0 / float(tp_count)] * tp_count if tp_count > 0 else []
        except Exception:
            return [1.0 / float(tp_count)] * tp_count if tp_count > 0 else []
        
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
                # Simulate tracking for testing mode
                if signal_data['action'] == 'BUY':
                    entries = signal_data.get('entries')
                    take_profits = signal_data.get('take_profits')
                    self.active_trades[signal_data['symbol']] = {
                        'entry_price': float(signal_data['price']) if not entries else float(entries[0]),
                        'entries': [float(p) for p in entries] if entries else None,
                        'take_profits': [float(p) for p in take_profits] if take_profits else None,
                        'tp_filled': [False] * len(take_profits) if take_profits else None,
                        'stop_loss': float(signal_data['stop_loss']) if 'stop_loss' in signal_data else None,
                        'position_size': 0,
                        'leverage': float(signal_data.get('leverage', self.config['leverage'])),
                        'order_type': signal_data.get('order_type', 'LIMIT').upper(),
                        'timestamp': datetime.now(),
                        'tx_hash': None
                    }
                logging.warning("Contracts not loaded - signal tracked but not executed")
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
            order_type = signal_data.get('order_type', 'LIMIT').upper()
            
            # Get market info
            market_info = self.get_market_info(symbol)
            if not market_info:
                logging.error(f"Market info not found for {symbol}")
                return False
            
            entries: Optional[list] = signal_data.get('entries')
            take_profits: Optional[list] = signal_data.get('take_profits')
            tx_hashes = []
            total_position_size = 0
            avg_price_accumulator = 0.0
            
            if entries and order_type == 'LIMIT':
                # Laddered limit entries
                logging.info(f"Placing laddered entries for {symbol}: {entries}")
                for entry_str in entries:
                    execution_price = float(entry_str)
                    position_size = self.get_position_size(symbol, execution_price) // len(entries)
                    if position_size == 0:
                        logging.error("Invalid position size for ladder entry")
                        continue
                    transaction = self.exchange.functions.openPosition(
                        market_info['id'],
                        int(position_size),
                        int(execution_price * 1e6),
                        self.config['leverage'],
                        True
                    ).build_transaction({
                        'from': self.account.address,
                        'gas': 500000,
                        'gasPrice': self.w3.eth.gas_price,
                        'nonce': self.w3.eth.get_transaction_count(self.account.address),
                        'chainId': 42161
                    })
                    signed_txn = self.w3.eth.account.sign_transaction(transaction, self.config['private_key'])
                    tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
                    receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                    if receipt['status'] == 1:
                        tx_hashes.append(tx_hash.hex())
                        total_position_size += int(position_size)
                        avg_price_accumulator += execution_price * int(position_size)
                        logging.info(f"Ladder entry executed at ${execution_price}: {tx_hash.hex()}")
                    else:
                        logging.error(f"Ladder entry failed at ${execution_price}")
                if total_position_size == 0:
                    return False
                avg_entry_price = avg_price_accumulator / total_position_size
                self.active_trades[symbol] = {
                    'entry_price': avg_entry_price,
                    'entries': [float(p) for p in entries],
                    'position_size': total_position_size,
                    'initial_position_size': total_position_size,
                    'leverage': self.config['leverage'],
                    'order_type': order_type,
                    'timestamp': datetime.now(),
                    'tx_hash': tx_hashes,
                    'take_profits': [float(p) for p in take_profits] if take_profits else None,
                    'tp_filled': [False] * len(take_profits) if take_profits else None,
                    'stop_loss': float(signal_data['stop_loss']) if 'stop_loss' in signal_data else None
                }
                return True
            else:
                # Single entry (market or limit)
                if order_type == 'MARKET':
                    current_price = float(market_info.get('price', 0))
                    if current_price == 0:
                        logging.error(f"Could not get current market price for {symbol}")
                        return False
                    execution_price = current_price
                    logging.info(f"Market order: Using current price ${current_price} for {symbol}")
                else:
                    execution_price = float(signal_data['price'])
                    logging.info(f"Limit order: Using specified price ${execution_price} for {symbol}")
                position_size = self.get_position_size(symbol, execution_price)
                if position_size == 0:
                    logging.error("Invalid position size")
                    return False
                transaction = self.exchange.functions.openPosition(
                    market_info['id'],
                    position_size,
                    int(execution_price * 1e6),
                    self.config['leverage'],
                    True
                ).build_transaction({
                    'from': self.account.address,
                    'gas': 500000,
                    'gasPrice': self.w3.eth.gas_price,
                    'nonce': self.w3.eth.get_transaction_count(self.account.address),
                    'chainId': 42161
                })
                signed_txn = self.w3.eth.account.sign_transaction(transaction, self.config['private_key'])
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                if receipt['status'] == 1:
                    self.active_trades[symbol] = {
                        'entry_price': execution_price,
                        'entries': None,
                        'position_size': position_size,
                        'initial_position_size': position_size,
                        'leverage': self.config['leverage'],
                        'order_type': order_type,
                        'timestamp': datetime.now(),
                        'tx_hash': tx_hash.hex(),
                        'take_profits': [float(p) for p in take_profits] if take_profits else None,
                        'tp_filled': [False] * len(take_profits) if take_profits else None,
                        'stop_loss': float(signal_data['stop_loss']) if 'stop_loss' in signal_data else None
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
            order_type = signal_data.get('order_type', 'LIMIT').upper()
            
            # Check if we have an active position
            if symbol not in self.active_trades:
                logging.error("No active position to sell")
                return False
            
            # Get market info
            market_info = self.get_market_info(symbol)
            if not market_info:
                logging.error(f"Market info not found for {symbol}")
                return False
            
            # Handle market vs limit orders
            if order_type == 'MARKET':
                # For market orders, get current market price
                current_price = float(market_info.get('price', 0))
                if current_price == 0:
                    logging.error(f"Could not get current market price for {symbol}")
                    return False
                
                execution_price = current_price
                logging.info(f"Market sell order: Using current price ${current_price} for {symbol}")
            else:
                # For limit orders, use the specified price
                execution_price = float(signal_data['price'])
                logging.info(f"Limit sell order: Using specified price ${execution_price} for {symbol}")
            
            # Determine size to close (support partial close)
            sell_fraction = float(signal_data.get('sell_fraction', 1.0))
            sell_fraction = max(0.0, min(1.0, sell_fraction))
            current_position_size = int(self.active_trades[symbol]['position_size'])
            size_to_close = int(current_position_size * sell_fraction)
            if size_to_close <= 0:
                logging.error("Computed close size is zero; skipping sell")
                return False
            
            # Build transaction
            transaction = self.exchange.functions.closePosition(
                market_info['id'],
                size_to_close,
                int(execution_price * 1e6)  # Convert price to 6 decimals
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
                # Calculate profit/loss (approximate for partial)
                entry_price = self.active_trades[symbol]['entry_price']
                exit_price = execution_price
                profit_percentage = (exit_price - entry_price) / entry_price * self.config['leverage']
                logging.info(f"Sell order executed successfully: {tx_hash.hex()}")
                logging.info(f"Profit/Loss (per unit): {profit_percentage:.2%}")
                # Update position size / close trade if fully exited
                remaining = current_position_size - size_to_close
                if remaining <= 0:
                    del self.active_trades[symbol]
                else:
                    self.active_trades[symbol]['position_size'] = remaining
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
                
                # Stop loss by absolute level if provided, else by percentage
                if trade.get('stop_loss') is not None:
                    if current_price <= float(trade['stop_loss']):
                        logging.info(f"Stop loss level hit for {symbol} at ${current_price}")
                        self.execute_sell({
                            'action': 'SELL',
                            'symbol': symbol,
                            'price': current_price,
                            'order_type': 'MARKET'
                        })
                        continue
                else:
                    profit_percentage = (current_price - trade['entry_price']) / trade['entry_price'] * trade['leverage']
                    if profit_percentage <= -self.config['stop_loss_percentage']:
                        logging.info(f"Stop loss percentage triggered for {symbol}")
                        self.execute_sell({
                            'action': 'SELL',
                            'symbol': symbol,
                            'price': current_price,
                            'order_type': 'MARKET'
                        })
                        continue
                
                # Multiple take profits support
                if trade.get('take_profits') and trade.get('tp_filled'):
                    tp_levels = trade['take_profits']
                    fractions = self._parse_tp_fractions(len(tp_levels))
                    initial_size = int(trade.get('initial_position_size', trade['position_size']))
                    current_size = int(trade['position_size'])
                    closed_so_far = max(initial_size - current_size, 0)
                    for idx, tp in enumerate(tp_levels):
                        if not trade['tp_filled'][idx] and current_price >= float(tp):
                            logging.info(f"TP{idx+1} hit for {symbol} at ${current_price} (target ${tp})")
                            # Compute target close size based on original position
                            target_for_this_tp = int(initial_size * float(fractions[idx]))
                            size_to_close = max(0, min(current_size, target_for_this_tp))
                            if size_to_close <= 0 or current_size <= 0:
                                trade['tp_filled'][idx] = True
                                continue
                            sell_fraction = float(size_to_close) / float(current_size)
                            self.execute_sell({
                                'action': 'SELL',
                                'symbol': symbol,
                                'price': current_price,
                                'order_type': 'MARKET',
                                'sell_fraction': sell_fraction
                            })
                            # Mark TP as filled if position still exists
                            if symbol in self.active_trades:
                                self.active_trades[symbol]['tp_filled'][idx] = True
                            break
                else:
                    # Legacy min profit threshold
                    profit_percentage = (current_price - trade['entry_price']) / trade['entry_price'] * trade['leverage']
                    if profit_percentage >= self.config['min_profit_threshold']:
                        logging.info(f"Take profit triggered for {symbol}")
                        self.execute_sell({
                            'action': 'SELL',
                            'symbol': symbol,
                            'price': current_price,
                            'order_type': 'MARKET'
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