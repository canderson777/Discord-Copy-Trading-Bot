import discord
from discord.ext import commands
import asyncio
import re
import os
from dotenv import load_dotenv
import logging
from copy_trader import LighterTrader

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for troubleshooting
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_trader.log'),
        logging.StreamHandler()
    ]
)

class DiscordTraderBot:
    def __init__(self):
        # Initialize the Lighter trader
        self.trader = LighterTrader()
        
        # Discord bot configuration
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        
        # Configuration
        self.config = {
            'discord_token': os.getenv('DISCORD_BOT_TOKEN'),
            'channel_id': int(os.getenv('TRADING_CHANNEL_ID')) if os.getenv('TRADING_CHANNEL_ID') else None,
            'trader_user_id': int(os.getenv('TRADER_USER_ID')) if os.getenv('TRADER_USER_ID') else None,
            'auto_execute': os.getenv('AUTO_EXECUTE', 'false').lower() == 'true'
        }
        
        # Setup bot events
        self.setup_bot_events()
    
    def setup_bot_events(self):
        @self.bot.event
        async def on_ready():
            logging.info(f'{self.bot.user} has connected to Discord!')
            
        @self.bot.event
        async def on_message(message):
            try:
                # Don't respond to bot messages
                if message.author.bot:
                    return
                
                # Log all messages for debugging (only in specified channel)
                if self.config['channel_id'] and message.channel.id == self.config['channel_id']:
                    logging.debug(f"Channel message from {message.author.display_name}: {message.content}")
                
                # Check if message is from the specified channel
                if self.config['channel_id'] and message.channel.id != self.config['channel_id']:
                    return
                
                # Check if message is from the specified trader
                if self.config['trader_user_id'] and message.author.id != self.config['trader_user_id']:
                    logging.debug(f"Ignoring message from {message.author.display_name} (not target trader)")
                    return
                
                # Parse the message for trade signals
                signal = self.parse_trade_message(message.content)
                
                # If no signal found, try parsing multi-line format
                if not signal:
                    signal = self.parse_multiline_signal(message.content)
                else:
                    # If a single-line signal was found but message contains extra lines (SL/TP),
                    # merge supplemental fields from supplemental parsing.
                    if '\n' in message.content or any(tag in message.content.upper() for tag in ['SL', 'STOP', 'TP', 'TAKE PROFIT', 'TARGET']):
                        supplemental = self.parse_signal_supplement(message.content)
                        if supplemental:
                            for key in ['stop_loss', 'take_profit', 'take_profits', 'entries', 'leverage']:
                                if key in supplemental and key not in signal:
                                    signal[key] = supplemental[key]
                
                if signal:
                    logging.info(f"✅ Trade signal detected from {message.author.display_name}: {signal}")
                    
                    if self.config['auto_execute']:
                        # Auto-execute the trade
                        try:
                            success = self.trader.receive_trade_signal(signal)
                            if success:
                                await message.add_reaction('✅')
                                await message.reply(f"✅ Trade executed: {signal['action']} {signal['symbol']}")
                            else:
                                await message.add_reaction('❌')
                                await message.reply("❌ Failed to execute trade")
                        except Exception as e:
                            logging.error(f"Error executing trade: {str(e)}")
                            await message.add_reaction('❌')
                            await message.reply(f"❌ Error: {str(e)}")
                    else:
                        # Ask for confirmation
                        await message.add_reaction('🤔')
                        # Build pricing/TP details
                        entries_line = None
                        if 'entries' in signal:
                            entries_fmt = ' / '.join([f"${p}" for p in signal['entries']])
                            entries_line = f"Entries: {entries_fmt}\n"
                        price_line = f"Price: ${signal['price']}\n" if 'price' in signal else ''
                        tps_line = None
                        if 'take_profits' in signal:
                            tps_fmt = ' / '.join([f"${p}" for p in signal['take_profits']])
                            tps_line = f"TPs: {tps_fmt}\n"
                        tp_single_line = f"TP: ${signal.get('take_profit')}\n" if 'take_profit' in signal and 'take_profits' not in signal else ''
                        sl_line = f"Stop Loss: ${signal.get('stop_loss')}\n" if 'stop_loss' in signal else ''
                        details = (entries_line or price_line) + (tps_line or tp_single_line) + sl_line
                        confirmation_msg = await message.reply(
                            f"📊 **Trade Signal Detected**\n"
                            f"Order Type: {signal.get('order_type', 'LIMIT')}\n"
                            f"Action: {signal['action']}\n"
                            f"Symbol: {signal['symbol']}\n"
                            f"{details}"
                            f"Leverage: {signal.get('leverage', 'default')}\n\n"
                            f"React with ✅ to execute or ❌ to ignore"
                        )
                        await confirmation_msg.add_reaction('✅')
                        await confirmation_msg.add_reaction('❌')
                else:
                    # Log messages that weren't recognized as signals
                    if len(message.content) > 10:  # Only log substantial messages
                        logging.debug(f"❌ No signal detected in: '{message.content}'")
                
                # Process commands
                await self.bot.process_commands(message)
                
            except Exception as e:
                logging.error(f"Error processing message: {str(e)}")
                try:
                    await message.add_reaction('⚠️')
                except:
                    pass
        
        @self.bot.event
        async def on_reaction_add(reaction, user):
            # Don't respond to bot reactions
            if user.bot:
                return
            
            # Check if it's a confirmation reaction
            if reaction.emoji == '✅' and "Trade Signal Detected" in reaction.message.content:
                # Extract signal from the message
                signal = self.extract_signal_from_confirmation(reaction.message.content)
                if signal:
                    success = self.trader.receive_trade_signal(signal)
                    if success:
                        await reaction.message.edit(content=reaction.message.content + "\n\n✅ **EXECUTED**")
                    else:
                        await reaction.message.edit(content=reaction.message.content + "\n\n❌ **FAILED**")
            
            elif reaction.emoji == '❌' and "Trade Signal Detected" in reaction.message.content:
                await reaction.message.edit(content=reaction.message.content + "\n\n❌ **IGNORED**")
        
        # Register bot commands within the bot context so they're discovered
        @self.bot.command(name='status')
        async def status_command(ctx):
            """Check bot and trader status"""
            active_trades = len(self.trader.active_trades)
            trading_enabled = not self.trader.simulation_mode
            
            embed = discord.Embed(
                title="🤖 Copy Trader Status",
                color=0x00ff00 if trading_enabled else 0xff9900
            )
            embed.add_field(name="Trading Mode", value="🟢 Live Trading" if trading_enabled else "🟡 Testing Mode", inline=True)
            embed.add_field(name="Active Trades", value=str(active_trades), inline=True)
            embed.add_field(name="Auto Execute", value="✅" if self.config['auto_execute'] else "❌", inline=True)
            
            if not trading_enabled:
                embed.add_field(
                    name="⚠️ Notice", 
                    value="Bot is in testing mode. Signals will be detected but not executed. Configure contract addresses to enable trading.", 
                    inline=False
                )
            
            if self.trader.active_trades:
                trades_info = ""
                for symbol, trade in self.trader.active_trades.items():
                    if trade.get('entries'):
                        entries_fmt = ' / '.join([str(p) for p in trade['entries']])
                        trades_info += f"{symbol}: entries {entries_fmt} (avg ${trade['entry_price']:.2f})\n"
                    else:
                        trades_info += f"{symbol}: ${trade['entry_price']}\n"
                embed.add_field(name="Positions", value=trades_info, inline=False)
            
            await ctx.send(embed=embed)
        
        @self.bot.command(name='toggle_auto')
        async def toggle_auto_execute(ctx):
            """Toggle auto-execution of trades"""
            self.config['auto_execute'] = not self.config['auto_execute']
            status = "enabled" if self.config['auto_execute'] else "disabled"
            await ctx.send(f"🔄 Auto-execution {status}")
        
        @self.bot.command(name='close')
        async def close_position(ctx, symbol: str, price: float = None):
            """Manually close a position. If price omitted, closes at market."""
            sym = symbol.upper()
            if sym in self.trader.active_trades:
                # Build signal for market or limit close
                if price is None:
                    signal = {
                        'action': 'SELL',
                        'symbol': sym,
                        'price': '0',            # placeholder to satisfy validation
                        'order_type': 'MARKET'   # execute at current market price
                    }
                else:
                    signal = {
                        'action': 'SELL',
                        'symbol': sym,
                        'price': str(price),
                        'order_type': 'LIMIT'
                    }
                success = self.trader.receive_trade_signal(signal)
                if success:
                    if price is None:
                        await ctx.send(f"✅ Closed {symbol} at market")
                    else:
                        await ctx.send(f"✅ Closed {symbol} position at ${price}")
                else:
                    await ctx.send(f"❌ Failed to close {symbol} position")
            else:
                await ctx.send(f"❌ No active position for {symbol}")
    
    def parse_trade_message(self, message_content: str) -> dict:
        """Parse Discord message to extract trade signals"""
        message = message_content.upper()
        
        # Common trading signal patterns (ordered from most specific to general)
        patterns = [
            # Pattern 1: "Buy Now ETH" or "Buy Now BTC 30X" (NEW - MOST SPECIFIC)
            r'BUY\s+NOW\s+(\w+)(?:\s+(\d+)X)?',
            
            # Pattern 2a: "Market LONG BTC" or "Market SHORT ETH" (NEW - WITH SYMBOL)
            r'MARKET\s+(LONG|SHORT)\s+(\w+)',

            # Pattern 2b: "Market LONG" or "Market SHORT" (NEW - DEFAULTS TO BTC)
            r'MARKET\s+(LONG|SHORT)',
            
            # Pattern 3: "Market Buy BTC 50000" or "Limit Sell ETH 3000"
            r'(MARKET|LIMIT)\s+(BUY|SELL|LONG|SHORT)\s+(\w+)\s+\$?(\d+(?:\.\d+)?)',
            
            # Pattern 4: "🚀 Market Long BTC $50000" or "📈 Limit Short ETH 3000"
            r'(?:🚀|📈|📊)?\s*(MARKET|LIMIT)\s+(LONG|SHORT|BUY|SELL)\s+(\w+)\s+\$?(\d+(?:\.\d+)?)',
            
            # Pattern 5: "SIGNAL: BUY BTC $50000"
            r'SIGNAL:?\s+(BUY|SELL|LONG|SHORT)\s+(\w+)\s*\$?(\d+(?:\.\d+)?)',
            
            # Pattern 6: "Position: LONG BTC ENTRY $50000"
            r'POSITION:?\s+(LONG|SHORT)\s+(\w+)\s+(?:ENTRY:?)?\s*\$?(\d+(?:\.\d+)?)',
            
            # Pattern 7: "BUY BTC AT 50000" or "SELL ETH @ 3000"
            r'(BUY|SELL|LONG|SHORT)\s+(\w+)\s+(?:AT|@)\s*\$?(\d+(?:\.\d+)?)',
            
            # Pattern 8: "BTC BUY 50000" or "ETH LONG $3000"  
            r'(\w+)\s+(BUY|SELL|LONG|SHORT)\s+\$?(\d+(?:\.\d+)?)',
            
            # Pattern 9: "🚀 BTC LONG ENTRY: $50000"
            r'(?:🚀|📈|📊)?\s*(\w+)\s+(LONG|SHORT|BUY|SELL)\s+(?:ENTRY:?)?\s*\$?(\d+(?:\.\d+)?)',
            
            # Pattern 10: "SHORT SOL 150" or "LONG BTC 50000"
            r'(LONG|SHORT)\s+(\w+)\s+(\d+(?:\.\d+)?)',
            
            # Pattern 11: "SELL ETHEREUM 3000"
            r'(BUY|SELL)\s+(\w+)\s+(\d+(?:\.\d+)?)',
            
            # Pattern 12: Handle "50k", "3k" etc. (LEAST SPECIFIC)
            r'(BUY|SELL|LONG|SHORT)\s+(\w+)\s+(?:AT|@)?\s*\$?(\d+(?:\.\d+)?)[KkMm]?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                groups = match.groups()
                
                # Determine action and symbol based on pattern
                if len(groups) == 1:
                    # Pattern 2: "Market LONG" or "Market SHORT"
                    if groups[0] in ['LONG', 'SHORT']:
                        action = groups[0]
                        symbol = 'BTC'  # Default to BTC for market long/short
                        price = '0'  # Will use current market price
                        order_type = 'MARKET'
                    else:
                        continue
                elif len(groups) == 2:
                    # Pattern 2a: "Market LONG <SYMBOL>" or "Market SHORT <SYMBOL>"
                    if groups[0] in ['LONG', 'SHORT'] and 'MARKET' in message:
                        action = groups[0]
                        symbol = groups[1]
                        price = '0'  # Will use current market price
                        order_type = 'MARKET'
                        leverage = '2.0'
                    # Pattern 1: "Buy Now ETH" or "Buy Now BTC 30X"
                    elif groups[0] and groups[1] and groups[1].isdigit():
                        # "Buy Now BTC 30X" format
                        symbol = groups[0]
                        leverage = groups[1]
                        action = 'BUY'
                        price = '0'  # Will use current market price
                        order_type = 'MARKET'
                    elif groups[0]:
                        # "Buy Now ETH" format
                        symbol = groups[0]
                        action = 'BUY'
                        price = '0'  # Will use current market price
                        order_type = 'MARKET'
                        leverage = '2.0'  # Default leverage
                    else:
                        continue
                elif len(groups) == 3:
                    if groups[0] in ['BUY', 'SELL', 'LONG', 'SHORT']:
                        action, symbol, price = groups
                    else:
                        symbol, action, price = groups
                elif len(groups) == 4:
                    # Pattern 3: "Market Buy BTC 50000" or Pattern 4: "🚀 Market Long BTC $50000"
                    if groups[0] in ['MARKET', 'LIMIT']:
                        order_type, action, symbol, price = groups
                    else:
                        # Skip this pattern if it doesn't match order type format
                        continue
                else:
                    continue
                
                # Set order type for patterns that detected it
                if len(groups) == 4 and groups[0] in ['MARKET', 'LIMIT']:
                    order_type = groups[0].upper()
                elif len(groups) == 1 and groups[0] in ['LONG', 'SHORT']:
                    order_type = 'MARKET'  # Market LONG/SHORT pattern
                elif len(groups) == 2 and groups[0]:  # Buy Now patterns
                    order_type = 'MARKET'  # Buy Now patterns are always market orders
                else:
                    order_type = 'LIMIT'  # Default for single-line signals
                
                # Debug logging
                logging.debug(f"Pattern matched: {groups}, Order type: {order_type}")
                
                # Normalize action
                if action in ['LONG', 'BUY']:
                    action = 'BUY'
                elif action in ['SHORT', 'SELL']:
                    action = 'SELL'
                
                # Handle price multipliers (K, M)
                price_str = price
                if message.find(price + 'K') != -1:
                    price = str(float(price) * 1000)
                elif message.find(price + 'M') != -1:
                    price = str(float(price) * 1000000)
                
                # Extract leverage if mentioned
                leverage_match = re.search(r'(\d+)X|LEVERAGE[:\s]*(\d+)', message)
                leverage = '2.0'  # default
                if leverage_match:
                    leverage = leverage_match.group(1) or leverage_match.group(2)
                
                # Override leverage for Buy Now patterns if specified
                if len(groups) == 2 and groups[1] and groups[1].isdigit():
                    leverage = groups[1]  # Use leverage from "Buy Now BTC 30X"
                
                # Order type is already set above based on pattern type
                
                return {
                    'action': action,
                    'symbol': symbol,
                    'price': price,
                    'leverage': leverage,
                    'order_type': order_type
                }
        
        return None
    
    def parse_multiline_signal(self, message_content: str) -> dict:
        """Parse multi-line trading signals like:
        Limit Long BTC: 117320
        Stop Loss: 116690
        TP: 118900
        """
        lines = message_content.strip().split('\n')
        if len(lines) < 2:
            return None
        
        signal = {}
        
        # Parse each line
        for line in lines:
            line = line.strip().upper()
            
            # Main signal line patterns
            if any(word in line for word in ['LIMIT', 'MARKET']) and any(word in line for word in ['LONG', 'SHORT', 'BUY', 'SELL']):
                # "Limit Long BTC: 117320" or "Market Buy ETH: 3200"
                match = re.search(r'(LIMIT|MARKET)?\s*(LONG|SHORT|BUY|SELL)\s+(\w+)[:,]?\s*([\d\./\s]+)', line)
                if match:
                    order_type, action, symbol, price_part = match.groups()
                    
                    # Set order type (default to LIMIT if not specified)
                    if order_type:
                        signal['order_type'] = order_type.upper()
                    else:
                        signal['order_type'] = 'LIMIT'  # Default to limit order
                    
                    # Normalize action
                    if action in ['LONG', 'BUY']:
                        signal['action'] = 'BUY'
                    elif action in ['SHORT', 'SELL']:
                        signal['action'] = 'SELL'
                    
                    signal['symbol'] = symbol
                    # Extract one or multiple prices
                    prices_found = re.findall(r'(\d+(?:\.\d+)?)', price_part)
                    if len(prices_found) > 1:
                        signal['entries'] = prices_found
                        signal['price'] = prices_found[0]
                    elif len(prices_found) == 1:
                        signal['price'] = prices_found[0]
            
            # Alternative main signal patterns
            elif ':' in line and any(word in line for word in ['LONG', 'SHORT', 'BUY', 'SELL']):
                # "BTC LONG: 117320" or "ETH BUY: 3200" or "Short SOL: 150"
                patterns = [
                    r'(\w+)\s+(LONG|SHORT|BUY|SELL)[:,]\s*([\d\./\s]+)',
                    r'(LONG|SHORT|BUY|SELL)\s+(\w+)[:,]\s*([\d\./\s]+)'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, line)
                    if match:
                        groups = match.groups()
                        if len(groups) == 3:
                            if groups[0] in ['LONG', 'SHORT', 'BUY', 'SELL']:
                                action, symbol, price_part = groups
                            else:
                                symbol, action, price_part = groups
                            
                            # Normalize action
                            if action in ['LONG', 'BUY']:
                                signal['action'] = 'BUY'
                            elif action in ['SHORT', 'SELL']:
                                signal['action'] = 'SELL'
                            
                            signal['symbol'] = symbol
                            prices_found = re.findall(r'(\d+(?:\.\d+)?)', price_part)
                            if len(prices_found) > 1:
                                signal['entries'] = prices_found
                                signal['price'] = prices_found[0]
                            elif len(prices_found) == 1:
                                signal['price'] = prices_found[0]
                            break
            
            # Explicit entries line
            elif any(word in line for word in ['ENTRY', 'ENTRIES']):
                prices_found = re.findall(r'(\d+(?:\.\d+)?)', line)
                if prices_found:
                    if len(prices_found) > 1:
                        signal['entries'] = prices_found
                        signal['price'] = prices_found[0]
                    elif len(prices_found) == 1:
                        signal['price'] = prices_found[0]
            
            # Stop loss line - multiple patterns
            elif any(phrase in line for phrase in ['STOP LOSS', 'STOP:', 'SL:']):
                match = re.search(r'(\d+(?:\.\d+)?)', line)
                if match:
                    signal['stop_loss'] = match.group(1)
            
            # Take profit line - multiple patterns  
            elif any(word in line for word in ['TP:', 'TAKE PROFIT', 'TARGET:', 'PROFIT:']):
                prices_found = re.findall(r'(\d+(?:\.\d+)?)', line)
                if prices_found:
                    if len(prices_found) > 1:
                        signal['take_profits'] = prices_found
                        signal['take_profit'] = prices_found[0]
                    else:
                        signal['take_profit'] = prices_found[0]
            
            # Leverage line
            elif any(word in line for word in ['LEVERAGE', 'LEV']):
                match = re.search(r'(\d+)X?', line)
                if match:
                    signal['leverage'] = match.group(1)
        
        # Return signal only if we have the minimum required fields
        if 'action' in signal and 'symbol' in signal and 'price' in signal:
            # Set default leverage if not specified
            if 'leverage' not in signal:
                signal['leverage'] = '2.0'
            
            logging.info(f"Multi-line signal parsed: {signal}")
            return signal
        
        return None

    def parse_signal_supplement(self, message_content: str) -> dict:
        """Extract supplemental fields (SL/TP/Entries/Leverage) from a message.
        Does not require action/symbol/price and can be safely merged into a
        pre-parsed single-line signal.
        """
        lines = message_content.strip().split('\n')
        supplement = {}
        for raw_line in lines:
            line = raw_line.strip().upper()
            if not line:
                continue
            # Stop loss
            if any(phrase in line for phrase in ['STOP LOSS', 'STOP:', 'SL:']):
                m = re.search(r'(\d+(?:\.\d+)?)', line)
                if m:
                    supplement['stop_loss'] = m.group(1)
                continue
            # Take profit(s)
            if any(word in line for word in ['TP:', 'TAKE PROFIT', 'TARGET:', 'PROFIT:']):
                prices_found = re.findall(r'(\d+(?:\.\d+)?)', line)
                if prices_found:
                    if len(prices_found) > 1:
                        supplement['take_profits'] = prices_found
                        supplement['take_profit'] = prices_found[0]
                    else:
                        supplement['take_profit'] = prices_found[0]
                continue
            # Entries
            if any(word in line for word in ['ENTRY', 'ENTRIES']):
                prices_found = re.findall(r'(\d+(?:\.\d+)?)', line)
                if prices_found:
                    if len(prices_found) > 1:
                        supplement['entries'] = prices_found
                    # Do not override 'price' here; single-line may be market
                continue
            # Leverage
            if any(word in line for word in ['LEVERAGE', 'LEV']):
                m = re.search(r'(\d+)X?', line)
                if m:
                    supplement['leverage'] = m.group(1)
                continue
        return supplement
    
    def extract_signal_from_confirmation(self, message_content: str) -> dict:
        """Extract signal from confirmation message"""
        lines = message_content.split('\n')
        signal = {}
        
        for line in lines:
            if line.startswith('Action:'):
                signal['action'] = line.split(':')[1].strip()
            elif line.startswith('Symbol:'):
                signal['symbol'] = line.split(':')[1].strip()
            elif line.startswith('Entries:'):
                prices_found = re.findall(r'(\d+(?:\.\d+)?)', line)
                if prices_found:
                    signal['entries'] = prices_found
                    signal['price'] = prices_found[0]
            elif line.startswith('TPs:'):
                prices_found = re.findall(r'(\d+(?:\.\d+)?)', line)
                if prices_found:
                    signal['take_profits'] = prices_found
                    signal['take_profit'] = prices_found[0]
            elif line.startswith('Price:'):
                price = line.split(':')[1].strip().replace('$', '')
                signal['price'] = price
            elif line.startswith('Leverage:'):
                leverage = line.split(':')[1].strip()
                if leverage != 'default':
                    signal['leverage'] = leverage
        
        return signal if len(signal) >= 3 else None
    
    
    def run(self):
        """Start the Discord bot"""
        if not self.config['discord_token']:
            logging.error("Discord bot token not found in environment variables")
            return
        
        logging.info("Starting Discord trader bot...")
        self.bot.run(self.config['discord_token'])

def main():
    # Start the Discord bot
    discord_bot = DiscordTraderBot()
    
    # Start position monitoring in background
    async def monitor_positions():
        while True:
            discord_bot.trader.check_positions()
            await asyncio.sleep(60)  # Check every minute
    
    # Run both the Discord bot and position monitoring
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Start position monitoring task
    loop.create_task(monitor_positions())
    
    # Start Discord bot
    discord_bot.run()

if __name__ == "__main__":
    main()
