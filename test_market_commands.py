#!/usr/bin/env python3
"""
Test script to verify new market order commands
"""
import sys
from discord_trader_bot import DiscordTraderBot

def test_market_commands():
    """Test the new market order commands"""
    print("🧪 Testing New Market Order Commands")
    print("=" * 50)
    
    try:
        # Initialize the bot
        bot = DiscordTraderBot()
        
        # Test the new market order commands
        test_commands = [
            # New Buy Now commands
            "Buy Now ETH",
            "Buy Now BTC",
            "Buy Now LINK",
            "Buy Now BTC 30X",
            "Buy Now ETH 10X",
            
            # New Market LONG/SHORT commands
            "Market LONG",
            "Market SHORT",
            "Market LONG TIA",
            "Market SHORT SOL",
            
            # Mixed case variations
            "buy now eth",
            "MARKET LONG",
            "market short",
            
            # With extra spaces
            "Buy Now  ETH  ",
            "  Market  LONG  ",
        ]
        
        for i, command in enumerate(test_commands, 1):
            print(f"\n{i}. Testing: '{command}'")
            
            # Try single-line parsing first
            signal = bot.parse_trade_message(command)
            if not signal:
                # Try multi-line parsing
                signal = bot.parse_multiline_signal(command)
            
            if signal:
                order_type = signal.get('order_type', 'LIMIT')
                price = signal.get('price', '0')
                leverage = signal.get('leverage', 'default')
                
                print(f"   ✅ DETECTED: {signal['action']} {signal['symbol']}")
                print(f"   📋 Order Type: {order_type}")
                print(f"   💰 Price: ${price} (market price will be used)")
                print(f"   ⚡ Leverage: {leverage}")
                
                # Verify it's a market order
                if order_type == 'MARKET':
                    print(f"   🎯 Market Order: Will execute at current price")
                else:
                    print(f"   ⚠️  Expected MARKET order type")
            else:
                print(f"   ❌ No signal detected")
        
        print("\n" + "=" * 50)
        print("✅ Market order commands test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_market_commands()
    sys.exit(0 if success else 1)
