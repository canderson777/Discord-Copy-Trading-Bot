# 🤖 Discord Copy Trader Bot

An advanced Discord bot that automatically detects and executes cryptocurrency trading signals from Discord messages. Perfect for copy trading from professional traders with sophisticated multi-line signal formats.

## ✨ Features

- 🎯 **Advanced Signal Detection** - Supports both single-line and complex multi-line trading signals
- 🛡️ **Risk Management** - Built-in stop-loss and take-profit handling
- ⚡ **Dual Modes** - Manual confirmation or auto-execution
- 📊 **Professional Format Support** - Handles sophisticated trading signals with leverage, SL, and TP
- 🔒 **Safe Testing Mode** - Test signal detection without executing real trades
- 📝 **Comprehensive Logging** - Full audit trail of all detected signals and actions

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/canderson777/Discord-Copy-Trader-Bot.git
cd discord-copy-trader-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configuration
1. Copy `env_example.txt` to `.env`
2. Fill in your Discord bot token and other settings
3. Get your Discord bot token from [Discord Developer Portal](https://discord.com/developers/applications)

### 4. Test Configuration
```bash
python test_config.py
```

### 5. Run the Bot
```bash
python discord_trader_bot.py
```

## 📊 Supported Signal Formats

### Multi-Line Professional Signals
```
Limit Long BTC: 117320
Stop Loss: 116690
TP: 118900
```

### Single-Line Signals
```
🚀 BTC LONG $50000 5X
SIGNAL: BUY ETH $3200
SHORT SOL 150
```

## 🎮 Bot Commands

- `!status` - Check bot status and active trades
- `!toggle_auto` - Toggle between manual/auto execution
- `!close SYMBOL [PRICE]` - Close position (market if price omitted)
- `!ping` - Check bot connection

## 🔧 Configuration

### Required Settings (API Mode)
```env
DISCORD_BOT_TOKEN=your_discord_bot_token
HYPERLIQUID_API_BASE=https://api.hyperliquid.xyz
HL_API_PRIVATE_KEY=your_hyperliquid_api_wallet_private_key
# Optional: set to true to use testnet endpoints if supported
HL_TESTNET=false
```

### Optional Settings
```env
TRADING_CHANNEL_ID=123456789012345678
TRADER_USER_ID=987654321098765432
AUTO_EXECUTE=false
MAX_POSITION_SIZE=0.2
LEVERAGE=2.0
TP_FRACTIONS=33/33/34
```

### Position Sizing (NEW!)

The bot now uses **percentage-based position sizing** for better risk management:

- `MAX_POSITION_SIZE=0.2` = 20% of your account balance
- `MAX_POSITION_SIZE=0.1` = 10% of your account balance  
- `MAX_POSITION_SIZE=0.05` = 5% of your account balance

**Example with $100 account:**
- `MAX_POSITION_SIZE=0.2` + `LEVERAGE=2.0` = $20 × 2x = $40 position
- `MAX_POSITION_SIZE=0.1` + `LEVERAGE=2.0` = $10 × 2x = $20 position

This automatically scales with your account size and prevents over-leveraging!

## 🧪 Testing Your Bot

### Step 1: Validate Configuration
```bash
python test_config.py
```
This will verify your Discord token and Hyperliquid API connectivity. If `HL_API_PRIVATE_KEY` is not set, the bot runs in simulation mode (no live trades).

### Step 2: Test Signal Parsing
```bash
python debug_discord.py
```
This tests message parsing without connecting to Discord.

### Step 3: Test Discord Connection
```bash
python simple_discord_test.py
```
Basic Discord connection test - press Ctrl+C to stop.

### Step 4: Run Full Bot Testing
```bash
python discord_trader_bot.py
```

### Step 5: Test in Discord
Once the bot is running, test these commands in your Discord channel:

**Basic Commands:**
- `!status` - Check bot status
- `!ping` - Test connection
- `!test` - Verify bot is responding

**Signal Testing:**
Post these messages to test signal detection:
```
BUY BTC AT 50000
SHORT ETH 3000 5X
🚀 SOL LONG $150
```

**Multi-line Signal Testing:**
```
Limit Long BTC: 117320
Stop Loss: 116690
TP: 118900
```

### Expected Bot Behavior
- Bot reacts with 🤔 to detected signals
- Shows confirmation message with signal details
- React with ✅ to confirm execution (safe - no real trades in testing mode)
- React with ❌ to ignore the signal

### Troubleshooting
- Check `discord_trader.log` for detailed logs
- Ensure bot has proper Discord permissions (Read Messages, Send Messages, Add Reactions)
- Verify you're testing in the correct channel (if TRADING_CHANNEL_ID is set)

## 🛡️ Safety Features

- **Testing Mode**: Detects signals without executing trades (default)
- **Manual Confirmation**: Ask for approval before executing trades
- **User Filtering**: Only listen to specified trader
- **Channel Filtering**: Monitor specific channels only
- **Position Limits**: Configurable percentage-based position sizing

## 📚 Documentation

- [Complete Trading Signals Guide](TRADING_SIGNALS_GUIDE.md)
- [Setup Instructions](setup_instructions.md)

### Take Profit Fractions (Partial Exits)

You can define how much of the original position to close at each TP level.

- Code location: `copy_trader.py`
  - Function: `_parse_tp_fractions`
  - Used by: `check_positions` when TP levels are hit
- Default behavior: Equal fractions across all TPs. With 3 TPs, defaults to ~33% each.
- Environment variable: `TP_FRACTIONS`

Accepted formats (they normalize to sum to 100%):

```env
# All equivalent examples for 3 TPs
TP_FRACTIONS=33/33/34
TP_FRACTIONS=33,33,34
TP_FRACTIONS=0.33/0.33/0.34
TP_FRACTIONS=25 50 25
```

Notes:
- If the number of fractions does not match the number of TP levels, the bot falls back to equal splits.
- Fractions apply to the ORIGINAL position size. The bot calculates a proportional close size for the current remaining position when each TP triggers.

## ⚠️ Disclaimer

This bot is for educational purposes. Trading cryptocurrencies involves significant risk. Always test thoroughly and never risk more than you can afford to lose.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Pull requests are welcome! Please read our contributing guidelines first.

## 📞 Support

- Create an issue for bug reports
- Join our Discord community for support
- Check the documentation for common questions
