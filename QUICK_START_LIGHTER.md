# 🚀 Quick Start: Lighter.xyz Trading Bot

Get your Discord copy trading bot running on Lighter.xyz in just a few steps!

## Prerequisites
- ✅ Python 3.11 installed
- ✅ Lighter.xyz private beta access
- ✅ Discord bot token
- ✅ Lighter API credentials

## 5-Minute Setup

### Step 1: Install Lighter SDK (2 minutes)
```bash
# Clone the Lighter SDK
git clone https://github.com/hangukquant/lighter_sdk
cd lighter_sdk
pip install -e .
cd ..
```

### Step 2: Install Dependencies (1 minute)
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment (2 minutes)
```bash
# Copy the example file
cp env_example.txt .env

# Edit the file (use your preferred editor)
nano .env
```

**Minimum required settings:**
```env
# Discord
DISCORD_BOT_TOKEN=your_discord_bot_token

# For simulation mode (testing), leave these empty:
API_KEY_PRIVATE_KEY=
ETH_PRIVATE_KEY=
LIGHTER_ACCOUNT_INDEX=

# For live trading, fill these in:
# API_KEY_PRIVATE_KEY=your_api_key
# ETH_PRIVATE_KEY=your_eth_private_key
# LIGHTER_ACCOUNT_INDEX=your_account_index
```

### Step 4: Run the Bot!
```bash
python discord_trader_bot.py
```

That's it! The bot is now running in simulation mode. 🎉

## Test It Out

Post these messages in your Discord channel:

```
BUY BTC AT 50000
```

```
Limit Long ETH: 3200
Stop Loss: 3150
TP: 3300
```

The bot should:
- React with 🤔 when it detects a signal
- Show a confirmation message
- Log the signal in `discord_trader.log`

## Going Live

Ready for real trading? Here's what you need:

### 1. Get Your Lighter Credentials

**API Key Private Key:**
- Log into Lighter.xyz
- Go to API settings
- Generate a new API key (use index 2 or higher)

**ETH Private Key:**
- Export from your Ethereum wallet
- This is your main wallet private key

**Account Index:**
Run this Python script:
```python
import requests
from eth_account import Account

# Replace with your ETH private key
eth_private_key = "0x..."

# Get your ETH address
account = Account.from_key(eth_private_key)
eth_address = account.address

# Query Lighter API
response = requests.get(
    f"https://api.lighter.xyz/accountsByL1Address?address={eth_address}"
)

if response.status_code == 200:
    data = response.json()
    account_index = data['sub_accounts'][0]
    print(f"✅ Your Account Index: {account_index}")
else:
    print(f"❌ Error: {response.text}")
```

### 2. Update Your .env File

```env
LIGHTER_API_BASE=https://api.lighter.xyz
API_KEY_PRIVATE_KEY=your_api_key_private_key_here
ETH_PRIVATE_KEY=your_eth_private_key_here
LIGHTER_ACCOUNT_INDEX=your_account_index_here
API_KEY_INDEX=2

DISCORD_BOT_TOKEN=your_discord_bot_token

# Start with manual confirmation
AUTO_EXECUTE=false

# Use 10% of account per trade
MAX_POSITION_SIZE=0.1
LEVERAGE=2.0
```

### 3. Restart the Bot

```bash
python discord_trader_bot.py
```

Now when signals are detected, the bot will:
1. Show confirmation message
2. Wait for you to react with ✅
3. Execute the trade on Lighter.xyz
4. Log everything to `discord_trader.log`

## Bot Commands

Use these commands in Discord:

| Command | Description |
|---------|-------------|
| `!status` | Check bot status and active trades |
| `!toggle_auto` | Toggle auto-execution on/off |
| `!close SYMBOL` | Close position at market price |
| `!close SYMBOL PRICE` | Close position at limit price |

## Supported Signal Formats

### Simple Signals
```
BUY BTC AT 50000
SELL ETH @ 3000
SHORT SOL 150
Market LONG BTC
```

### Professional Signals
```
Limit Long BTC: 50000
Stop Loss: 49000
TP: 52000 / 54000 / 56000
Leverage: 5X
```

### Laddered Entries
```
Long ETH
Entries: 3200 / 3150 / 3100
TP: 3400 / 3600
Stop Loss: 3050
```

## Configuration Tips

### Position Sizing
```env
# Use 10% of account balance per trade
MAX_POSITION_SIZE=0.1

# Use 20% of account balance per trade
MAX_POSITION_SIZE=0.2

# Use 5% of account balance per trade (conservative)
MAX_POSITION_SIZE=0.05
```

### Leverage
```env
# Conservative
LEVERAGE=2.0

# Moderate
LEVERAGE=5.0

# Aggressive (⚠️ high risk)
LEVERAGE=10.0
```

### Safety Settings
```env
# Manual confirmation (recommended for beginners)
AUTO_EXECUTE=false

# Auto-execution (only if you fully trust the signal source!)
AUTO_EXECUTE=true

# Stop loss at 5% loss
STOP_LOSS_PERCENTAGE=0.05

# Take profit at 2% gain (legacy, overridden by TP levels in signals)
MIN_PROFIT_THRESHOLD=0.02
```

## Directory Structure

```
Copy Trader Bot/
├── copy_trader.py              # Core trading logic (LighterTrader)
├── discord_trader_bot.py       # Discord bot integration
├── requirements.txt            # Python dependencies
├── .env                        # Your configuration (CREATE THIS!)
├── env_example.txt            # Example configuration
├── README.md                   # Main documentation
├── setup_instructions.md       # Detailed setup guide
├── LIGHTER_MIGRATION_GUIDE.md  # Migration details
├── MIGRATION_SUMMARY.md        # Migration overview
├── QUICK_START_LIGHTER.md     # This file
└── discord_trader.log         # Bot logs (auto-created)
```

## Troubleshooting

### Bot won't start
- Check `discord_trader.log` for errors
- Verify Discord token is correct
- Ensure Python 3.11 is installed

### Signals not detected
- Check `discord_trader.log` for parsing attempts
- Verify bot has permission to read messages
- Test with simple signals first: `BUY BTC AT 50000`

### Trades not executing
- Check if you're in simulation mode (missing API credentials)
- Verify Lighter credentials are correct
- Check account balance on Lighter.xyz
- Review `discord_trader.log` for specific errors

### "ModuleNotFoundError: No module named 'lighter'"
- Install the Lighter SDK from GitHub:
  ```bash
  git clone https://github.com/hangukquant/lighter_sdk
  cd lighter_sdk
  pip install -e .
  ```

## Safety Checklist

Before enabling auto-execution:

- [ ] Tested extensively in simulation mode
- [ ] Verified signal detection works correctly
- [ ] Set reasonable position sizes (start with 5-10%)
- [ ] Configured appropriate leverage (2-5x recommended)
- [ ] Tested with manual confirmation mode first
- [ ] Have stop-loss levels in all signals
- [ ] Monitoring logs regularly
- [ ] Understand the risks involved

## Next Steps

1. ✅ **Run in simulation mode** to test signal detection
2. ✅ **Get comfortable** with the bot's behavior
3. ✅ **Get Lighter credentials** when ready for live trading
4. ✅ **Start with manual confirmation** mode (`AUTO_EXECUTE=false`)
5. ✅ **Use small position sizes** initially (`MAX_POSITION_SIZE=0.05`)
6. ✅ **Monitor closely** for the first few trades
7. ✅ **Scale up gradually** as you gain confidence

## Resources

- 📖 [Lighter API Documentation](https://apidocs.lighter.xyz/docs/private-beta)
- 💻 [Lighter SDK GitHub](https://github.com/hangukquant/lighter_sdk)
- 📚 [Full Setup Guide](setup_instructions.md)
- 🔄 [Migration Guide](LIGHTER_MIGRATION_GUIDE.md)
- 📊 [Trading Signals Guide](TRADING_SIGNALS_GUIDE.md)

## Support

- Check `discord_trader.log` for detailed logs
- Review the [Lighter API Docs](https://apidocs.lighter.xyz/docs/private-beta)
- Join Lighter's Discord (#api-updates channel)
- Open an issue on GitHub

---

**Happy Trading! 🚀**

Remember: Start with simulation mode, use small positions, and always have stop-losses!

