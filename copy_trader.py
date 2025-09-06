import json
import time
from datetime import datetime
import logging
import re
from typing import Dict, Optional
import os
from dotenv import load_dotenv
import requests
try:
    # Hyperliquid SDK (installed via requirements)
    from hyperliquid.info import Info
    from hyperliquid.exchange import Exchange
    from hyperliquid.utils.signing import LocalWallet
    from hyperliquid.utils import constants as hl_constants
except Exception:
    # SDK not available at import time; we'll guard usage at runtime
    Info = None
    Exchange = None
    LocalWallet = None
    hl_constants = None

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
        # Load configuration and detect API mode
        load_dotenv()
        self.api_base = os.getenv('HYPERLIQUID_API_BASE', 'https://api.hyperliquid.xyz')
        self.hl_private_key = os.getenv('HL_API_PRIVATE_KEY')

        # Trading configuration
        self.config = {
            'max_position_size': float(os.getenv('MAX_POSITION_SIZE', '0.1')),
            'leverage': float(os.getenv('LEVERAGE', '2.0')),
            'min_profit_threshold': float(os.getenv('MIN_PROFIT_THRESHOLD', '0.02')),
            'stop_loss_percentage': float(os.getenv('STOP_LOSS_PERCENTAGE', '0.05')),
        }

        # Initialize Hyperliquid SDK if credentials provided; otherwise run in simulation mode
        self.simulation_mode = self.hl_private_key is None or Info is None or Exchange is None or LocalWallet is None
        self.info = None
        self.exchange = None
        self.wallet = None
        if not self.simulation_mode:
            try:
                # Prefer provided API base; fall back to SDK constants if possible
                base_url = self.api_base
                if hl_constants is not None:
                    # If user set TESTNET via env (optional), switch URL
                    use_testnet = os.getenv('HL_TESTNET', 'false').lower() == 'true'
                    base_url = hl_constants.TESTNET_API_URL if use_testnet else base_url
                self.info = Info(base_url, skip_ws=True)
                self.wallet = LocalWallet(self.hl_private_key)
                self.exchange = Exchange(self.wallet, base_url, self.info)
                logging.info("Hyperliquid SDK initialized - live trading enabled")
            except Exception as e:
                logging.warning(f"Failed to initialize Hyperliquid SDK, falling back to simulation mode: {str(e)}")
                self.simulation_mode = True

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
        """Retained for backward compatibility; no-op in API mode."""
        return True

    def get_market_info(self, symbol: str) -> Dict:
        """Get market information from Hyperliquid API.
        Falls back to REST call to /info if SDK is unavailable.
        """
        try:
            if self.info is not None:
                # Try to fetch price via SDK if available
                # Many SDKs expose mid prices via info or meta endpoints.
                # As a simple approach, fall back to REST which returns a list of markets.
                pass
            response = requests.get(f"{self.api_base}/info", timeout=5)
            if response.status_code == 200:
                markets = response.json()
                for market in markets:
                    if market.get('symbol') == symbol:
                        return market
            return None
        except Exception as e:
            logging.error(f"Error fetching market info: {str(e)}")
            return None

    def get_account_balance(self) -> float:
        """Get USDC balance from Hyperliquid account"""
        try:
            if self.simulation_mode or self.exchange is None:
                # In simulation mode, return a default balance for testing
                return 100.0  # Default $100 for simulation
            
            # Get account info from Hyperliquid
            if self.info is not None:
                # Try to get account info via SDK
                try:
                    # This is a placeholder - actual implementation depends on SDK methods
                    # You may need to adjust this based on the actual Hyperliquid SDK API
                    account_info = self.info.user_state(self.wallet.address)
                    if account_info and 'marginSummary' in account_info:
                        # Extract USDC balance from margin summary
                        margin_summary = account_info['marginSummary']
                        if 'accountValue' in margin_summary:
                            return float(margin_summary['accountValue'])
                except Exception as e:
                    logging.warning(f"Could not get balance via SDK: {str(e)}")
            
            # Fallback: try REST API
            try:
                response = requests.get(f"{self.api_base}/info", timeout=5)
                if response.status_code == 200:
                    # This is a simplified approach - you may need to adjust based on actual API
                    # For now, return a default value
                    logging.warning("Using default balance - implement proper balance retrieval")
                    return 100.0
            except Exception as e:
                logging.error(f"Error fetching balance via REST: {str(e)}")
            
            return 0.0
        except Exception as e:
            logging.error(f"Error getting account balance: {str(e)}")
            return 0.0

    def get_position_size(self, symbol: str, price: float) -> float:
        """Calculate position size in coin units based on percentage of account balance.
        MAX_POSITION_SIZE now represents the percentage of account balance to use (0.0-1.0).
        """
        try:
            # Get account balance in USDC
            account_balance = self.get_account_balance()
            if account_balance <= 0:
                logging.error("Account balance is zero or negative")
                return 0.0
            
            # MAX_POSITION_SIZE is now a percentage (0.0-1.0)
            position_percentage = float(self.config['max_position_size'])
            
            # Validate percentage
            if position_percentage <= 0 or position_percentage > 1.0:
                logging.error(f"Invalid position percentage: {position_percentage}. Must be between 0.0 and 1.0")
                return 0.0
            
            # Calculate USDC amount to use for this position
            usdc_to_use = account_balance * position_percentage
            
            # Apply leverage to get total position value
            leverage = float(self.config['leverage'])
            total_position_value = usdc_to_use * leverage
            
            # Convert to coin units
            coin_units = total_position_value / price
            
            logging.info(f"Position sizing: ${account_balance:.2f} balance × {position_percentage:.1%} = ${usdc_to_use:.2f} × {leverage}x leverage = ${total_position_value:.2f} position = {coin_units:.6f} {symbol}")
            
            return coin_units
            
        except Exception as e:
            logging.error(f"Error calculating position size: {str(e)}")
            return 0.0

    def receive_trade_signal(self, signal_data: Dict):
        """Process incoming trade signals"""
        try:
            # Validate signal data
            required_fields = ['action', 'symbol', 'price']
            if not all(field in signal_data for field in required_fields):
                logging.error("Invalid signal data: missing required fields")
                return False
            
            # If in simulation mode (no API credentials), log and simulate
            if self.simulation_mode:
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
                logging.warning("Simulation mode - signal tracked but not executed")
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
        """Execute a buy order using Hyperliquid SDK (or simulate if not available)."""
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
            order_refs = []
            total_position_size = 0.0
            avg_price_accumulator = 0.0
            
            if entries and order_type == 'LIMIT':
                # Laddered limit entries
                logging.info(f"Placing laddered entries for {symbol}: {entries}")
                for entry_str in entries:
                    execution_price = float(entry_str)
                    position_size = self.get_position_size(symbol, execution_price) / float(len(entries))
                    if position_size <= 0:
                        logging.error("Invalid position size for ladder entry")
                        continue
                    if self.simulation_mode or self.exchange is None:
                        order_refs.append({"simulated": True, "px": execution_price, "sz": position_size})
                        total_position_size += float(position_size)
                        avg_price_accumulator += execution_price * float(position_size)
                        logging.info(f"[SIM] Ladder entry at ${execution_price} for {position_size} {symbol}")
                    else:
                        order = {
                            "coin": symbol,
                            "is_buy": True,
                            "sz": position_size,
                            "limit_px": execution_price,
                            "order_type": {"limit": {"tif": "Gtc"}},
                            "reduce_only": False
                        }
                        resp = self.exchange.place_order(order)
                        order_refs.append(resp)
                        total_position_size += float(position_size)
                        avg_price_accumulator += execution_price * float(position_size)
                        logging.info(f"Ladder entry placed at ${execution_price}: {resp}")
                if total_position_size == 0:
                    return False
                avg_entry_price = avg_price_accumulator / total_position_size
                self.active_trades[symbol] = {
                    'entry_price': avg_entry_price,
                    'entries': [float(p) for p in entries],
                    'position_size': float(total_position_size),
                    'initial_position_size': float(total_position_size),
                    'leverage': self.config['leverage'],
                    'order_type': order_type,
                    'timestamp': datetime.now(),
                    'order_refs': order_refs,
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
                if position_size <= 0:
                    logging.error("Invalid position size")
                    return False
                if self.simulation_mode or self.exchange is None:
                    order_ref = {"simulated": True, "px": execution_price, "sz": position_size}
                    logging.info(f"[SIM] Buy {symbol} {position_size} @ ${execution_price}")
                else:
                    if order_type == 'MARKET':
                        # Emulate market by IOC limit at current price
                        order_type_payload = {"limit": {"tif": "Ioc"}}
                    else:
                        order_type_payload = {"limit": {"tif": "Gtc"}}
                    order = {
                        "coin": symbol,
                        "is_buy": True,
                        "sz": position_size,
                        "limit_px": execution_price,
                        "order_type": order_type_payload,
                        "reduce_only": False
                    }
                    order_ref = self.exchange.place_order(order)
                self.active_trades[symbol] = {
                    'entry_price': execution_price,
                    'entries': None,
                    'position_size': float(position_size),
                    'initial_position_size': float(position_size),
                    'leverage': self.config['leverage'],
                    'order_type': order_type,
                    'timestamp': datetime.now(),
                    'order_ref': order_ref,
                    'take_profits': [float(p) for p in take_profits] if take_profits else None,
                    'tp_filled': [False] * len(take_profits) if take_profits else None,
                    'stop_loss': float(signal_data['stop_loss']) if 'stop_loss' in signal_data else None
                }
                logging.info("Buy order placed")
                return True
                
        except Exception as e:
            logging.error(f"Error executing buy order: {str(e)}")
            return False

    def execute_sell(self, signal_data: Dict) -> bool:
        """Execute a sell/close order using Hyperliquid SDK (or simulate)."""
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
            current_position_size = float(self.active_trades[symbol]['position_size'])
            size_to_close = float(current_position_size * sell_fraction)
            if size_to_close <= 0:
                logging.error("Computed close size is zero; skipping sell")
                return False
            
            # Place reduce-only order (market via IOC limit)
            if self.simulation_mode or self.exchange is None:
                order_ref = {"simulated": True, "px": execution_price, "sz": size_to_close}
                logging.info(f"[SIM] Sell {symbol} {size_to_close} @ ${execution_price}")
            else:
                if order_type == 'MARKET':
                    order_type_payload = {"limit": {"tif": "Ioc"}}
                else:
                    order_type_payload = {"limit": {"tif": "Gtc"}}
                order = {
                    "coin": symbol,
                    "is_buy": False,
                    "sz": size_to_close,
                    "limit_px": execution_price,
                    "order_type": order_type_payload,
                    "reduce_only": True
                }
                order_ref = self.exchange.place_order(order)

            # Calculate profit/loss (approximate for partial)
            entry_price = self.active_trades[symbol]['entry_price']
            exit_price = execution_price
            profit_percentage = (exit_price - entry_price) / entry_price * self.config['leverage']
            logging.info(f"Sell order placed. P/L (per unit): {profit_percentage:.2%}")

            # Update position size / close trade if fully exited
            remaining = current_position_size - size_to_close
            if remaining <= 0:
                del self.active_trades[symbol]
            else:
                self.active_trades[symbol]['position_size'] = float(remaining)
            return True
                
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