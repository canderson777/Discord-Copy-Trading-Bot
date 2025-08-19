#!/usr/bin/env python3
"""
Discord debugging tool to help troubleshoot signal detection issues
"""
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

def check_discord_config():
    """Check Discord configuration"""
    print("🔍 Discord Configuration Check")
    print("=" * 40)
    
    # Check Discord bot token
    token = os.getenv('DISCORD_BOT_TOKEN')
    if token:
        print(f"✅ Discord Bot Token: {'*' * 20}{token[-4:]}")
    else:
        print("❌ Discord Bot Token: Missing")
        print("   Get this from Discord Developer Portal")
        return False
    
    # Check channel ID
    channel_id = os.getenv('TRADING_CHANNEL_ID')
    if channel_id:
        try:
            int(channel_id)
            print(f"✅ Trading Channel ID: {channel_id}")
        except ValueError:
            print(f"❌ Trading Channel ID: Invalid format ({channel_id})")
            print("   Should be a numeric Discord channel ID")
    else:
        print("⚠️  Trading Channel ID: Not set")
        print("   Bot will listen to ALL channels (may be noisy)")
    
    # Check trader user ID
    user_id = os.getenv('TRADER_USER_ID')
    if user_id:
        try:
            int(user_id)
            print(f"✅ Trader User ID: {user_id}")
        except ValueError:
            print(f"❌ Trader User ID: Invalid format ({user_id})")
            print("   Should be a numeric Discord user ID")
    else:
        print("⚠️  Trader User ID: Not set")
        print("   Bot will listen to ALL users (may be noisy)")
    
    # Check auto-execute setting
    auto_execute = os.getenv('AUTO_EXECUTE', 'false').lower()
    print(f"✅ Auto Execute: {auto_execute}")
    if auto_execute == 'true':
        print("   ⚠️  AUTO-EXECUTION IS ENABLED!")
    
    return True

def test_message_parsing():
    """Test message parsing with sample Discord messages"""
    print("\n🧪 Testing Common Discord Trading Messages")
    print("=" * 45)
    
    # Import the parsing function
    from discord_trader_bot import DiscordTraderBot
    bot = DiscordTraderBot()
    
    # Test messages that might appear in Discord
    test_messages = [
        # Standard formats
        "BUY BTC AT 50000",
        "SELL ETH 3000",
        "LONG SOL 150",
        "SHORT DOGE 0.08",
        
        # With symbols and emojis
        "🚀 BTC LONG $50000",
        "📈 ETH BUY 3200",
        "💰 SOL LONG ENTRY: $150",
        
        # Casual formats
        "btc long 50k",
        "eth buy $3000",
        "Going long BTC at 50000",
        
        # With leverage
        "BTC LONG 50000 5X",
        "SHORT ETH 3000 10X LEVERAGE",
        
        # Signal calls
        "SIGNAL: BUY BTC $50000",
        "Trade alert: LONG ETH 3200",
        
        # Position updates
        "Position: LONG BTC ENTRY $50000",
        "Opened: BTC LONG $50000",
        
        # Non-signals (should not match)
        "BTC is looking good",
        "Price target 50000",
        "What do you think about ETH?",
        "🚀🚀🚀 TO THE MOON",
    ]
    
    for i, message in enumerate(test_messages, 1):
        signal = bot.parse_trade_message(message)
        if signal:
            print(f"{i:2}. ✅ '{message}'")
            print(f"     → {signal['action']} {signal['symbol']} @ ${signal['price']} (Leverage: {signal['leverage']})")
        else:
            print(f"{i:2}. ❌ '{message}'")
        print()

def show_debugging_tips():
    """Show debugging tips"""
    print("\n🔧 Debugging Tips")
    print("=" * 20)
    print("1. Check the logs in 'discord_trader.log'")
    print("2. Enable debug logging by setting log level to DEBUG")
    print("3. Test with !status command in Discord")
    print("4. Make sure bot has 'Read Message History' permission")
    print("5. Verify the bot is in the correct channel")
    print("6. Check if the trader's user ID is correct")
    print("\n📝 To enable debug logging, add this to your code:")
    print("   logging.getLogger().setLevel(logging.DEBUG)")
    print("\n🤖 Discord Bot Permissions Needed:")
    print("   • Read Messages")
    print("   • Send Messages")  
    print("   • Add Reactions")
    print("   • Read Message History")

def main():
    print("🚀 Discord Copy Trader Bot Debugger")
    print("=" * 40)
    
    # Check configuration
    config_ok = check_discord_config()
    
    if config_ok:
        # Test message parsing
        test_message_parsing()
    
    # Show debugging tips
    show_debugging_tips()
    
    print("\n" + "=" * 40)
    if config_ok:
        print("✅ Configuration looks good!")
        print("🚀 Try running: python discord_trader_bot.py")
    else:
        print("❌ Fix configuration issues first")
        print("📝 Check your .env file")

if __name__ == "__main__":
    main()
