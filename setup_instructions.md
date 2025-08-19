# Discord Copy Trader Bot Setup

## Overview
This Discord integration allows your copy trader bot to automatically monitor Discord messages from a specific trader and execute trades based on their calls.

## Features
- 🤖 **Automatic Signal Detection**: Parses various trade signal formats
- ⚡ **Auto-Execute or Manual Confirm**: Choose between automatic execution or manual confirmation
- 📊 **Real-time Monitoring**: Monitors positions with stop-loss and take-profit
- 🔧 **Bot Commands**: Control the bot with Discord commands

## Setup Instructions

### 1. Create Discord Bot
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token
5. Enable "Message Content Intent" under Privileged Gateway Intents

### 2. Invite Bot to Server
1. Go to "OAuth2" > "URL Generator"
2. Select scopes: `bot`
3. Select permissions: `Send Messages`, `Read Message History`, `Add Reactions`
4. Use the generated URL to invite bot to your Discord server

### 3. Get Discord IDs
**Channel ID:**
1. Enable Developer Mode in Discord (User Settings > Advanced > Developer Mode)
2. Right-click the trading channel and "Copy ID"

**User ID:**
1. Right-click the trader's profile and "Copy ID"

### 4. Configure Environment
1. Copy `env_example.txt` to `.env`
2. Fill in all the required values:
   ```
   DISCORD_BOT_TOKEN=your_bot_token_here
   TRADING_CHANNEL_ID=123456789012345678
   TRADER_USER_ID=987654321098765432
   AUTO_EXECUTE=false  # Set to true for automatic execution
   ```

### 5. Install Dependencies
```bash
pip install -r requirements.txt
```

### 6. Run the Bot
```bash
python discord_trader_bot.py
```

## Supported Signal Formats

The bot can parse various trading signal formats:

✅ **"BUY BTC AT 50000"**
✅ **"SELL ETH @ $3000"** 
✅ **"BTC LONG $45000"**
✅ **"🚀 ETH LONG ENTRY: $3200"**
✅ **"SIGNAL: BUY BTC $48000"**
✅ **"SHORT SOL 150 5X"** (with leverage)

## Bot Commands

- `!status` - Check bot status and active trades
- `!toggle_auto` - Toggle auto-execution on/off
- `!close SYMBOL PRICE` - Manually close a position

## Safety Features

- **Manual Confirmation**: When auto-execute is off, bot asks for ✅/❌ confirmation
- **Reaction Feedback**: Bot reacts with ✅ for successful trades, ❌ for failures
- **User Filtering**: Only listens to specified trader's messages
- **Channel Filtering**: Only monitors the specified trading channel
- **Risk Management**: Built-in stop-loss and take-profit from original bot

## Usage Modes

### Manual Mode (Recommended for testing)
- Set `AUTO_EXECUTE=false`
- Bot will detect signals and ask for confirmation
- React with ✅ to execute or ❌ to ignore

### Auto Mode (For experienced users)
- Set `AUTO_EXECUTE=true`
- Bot automatically executes all detected signals
- ⚠️ **Use with caution** - ensure you trust the signal source

## Troubleshooting

1. **Bot not responding**: Check bot has proper permissions in the channel
2. **Signals not detected**: Verify the message format matches supported patterns
3. **Trades not executing**: Check your Hyperliquid configuration and wallet balance
4. **Wrong channel**: Verify `TRADING_CHANNEL_ID` is correct

## Security Notes

- Keep your `.env` file secure and never share it
- Start with `AUTO_EXECUTE=false` to test signal detection
- Monitor the logs in `discord_trader.log`
- The bot only executes trades from the specified user in the specified channel
