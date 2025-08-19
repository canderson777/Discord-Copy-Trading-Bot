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
git clone https://github.com/YOUR_USERNAME/discord-copy-trader-bot.git
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
- `!close SYMBOL PRICE` - Manually close a position
- `!ping` - Check bot connection

## 🔧 Configuration

### Required Settings
```env
DISCORD_BOT_TOKEN=your_discord_bot_token
ARBITRUM_RPC_URL=https://arb1.arbitrum.io/rpc
PRIVATE_KEY=your_wallet_private_key
```

### Optional Settings
```env
TRADING_CHANNEL_ID=123456789012345678
TRADER_USER_ID=987654321098765432
AUTO_EXECUTE=false
MAX_POSITION_SIZE=0.1
LEVERAGE=2.0
```

## 🛡️ Safety Features

- **Testing Mode**: Detects signals without executing trades (default)
- **Manual Confirmation**: Ask for approval before executing trades
- **User Filtering**: Only listen to specified trader
- **Channel Filtering**: Monitor specific channels only
- **Position Limits**: Configurable maximum position sizes

## 📚 Documentation

- [Complete Trading Signals Guide](TRADING_SIGNALS_GUIDE.md)
- [Setup Instructions](setup_instructions.md)

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
