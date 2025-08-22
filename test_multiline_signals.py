#!/usr/bin/env python3
"""
Test script for multi-line signal parsing
"""
from discord_trader_bot import DiscordTraderBot

def test_multiline_signals():
    """Test various multi-line signal formats"""
    print("🧪 Testing Multi-line Signal Parsing")
    print("=" * 50)
    
    # Create bot instance
    try:
        bot = DiscordTraderBot()
    except Exception:
        # If bot creation fails, create a minimal instance for testing
        class MockBot:
            def parse_multiline_signal(self, content):
                from discord_trader_bot import DiscordTraderBot
                temp_bot = DiscordTraderBot.__new__(DiscordTraderBot)
                return temp_bot.parse_multiline_signal(content)
        bot = MockBot()
    
    test_messages = [
        # Your exact format
        """Limit Long BTC: 117320
Stop Loss: 116690
TP: 118900""",
        
        # Variations
        """Market Buy ETH: 3200
Stop Loss: 3100
Take Profit: 3400""",
        
        """BTC LONG: 50000
STOP LOSS: 49000
TP: 52000
LEVERAGE: 5X""",
        
        """Short SOL: 150
Stop: 155
Target: 140""",
        
        # Single line (should not match)
        "BUY BTC AT 50000",
        
        # Incomplete multi-line
        """Long BTC: 50000
Some random text""",
        
        # With more details
        """📊 Trade Signal
Limit Long BTC: 117320
Stop Loss: 116690
TP: 118900
Risk: 2%""",
        
        # Alternative format
        """Entry: Long BTC 117320
SL: 116690
TP: 118900""",

        # With multiple entries and TPs
        """Limit Long BTC: 117320/116900/116500
SL: 116250
TP: 118900/119500/120000""",
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing message:")
        print("   " + message.replace('\n', '\n   '))
        
        try:
            signal = bot.parse_multiline_signal(message)
            if signal:
                print(f"   ✅ DETECTED: {signal['action']} {signal['symbol']} @ ${signal.get('price', 'n/a')}")
                if 'stop_loss' in signal:
                    print(f"       Stop Loss: ${signal['stop_loss']}")
                if 'entries' in signal:
                    print(f"       Entries: {' / '.join(signal['entries'])}")
                if 'take_profits' in signal:
                    print(f"       TPs: {' / '.join(signal['take_profits'])}")
                elif 'take_profit' in signal:
                    print(f"       Take Profit: ${signal['take_profit']}")
                if 'leverage' in signal:
                    print(f"       Leverage: {signal['leverage']}")
            else:
                print("   ❌ Not detected as multi-line signal")
        except Exception as e:
            print(f"   ⚠️  Error: {str(e)}")

if __name__ == "__main__":
    test_multiline_signals()
