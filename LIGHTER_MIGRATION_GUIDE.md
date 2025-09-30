# 🚀 Lighter.xyz Migration Guide

This document explains the migration from Hyperliquid to Lighter.xyz and provides setup instructions.

## What Changed?

### Core Changes
- ✅ Replaced `HyperliquidTrader` class with `LighterTrader` class
- ✅ Updated SDK from `hyperliquid-python-sdk` to `lighter_sdk`
- ✅ Changed authentication from single private key to API key + ETH private key
- ✅ Added account index system for wallet identification
- ✅ Updated all configuration files and documentation

### Files Modified
1. **copy_trader.py** - Complete rewrite with `LighterTrader` class
2. **discord_trader_bot.py** - Updated import from `HyperliquidTrader` to `LighterTrader`
3. **requirements.txt** - Removed Hyperliquid SDK, added Lighter SDK instructions
4. **env_example.txt** - Updated with Lighter.xyz credentials
5. **README.md** - Updated all references to Lighter.xyz
6. **setup_instructions.md** - Updated setup steps for Lighter.xyz

### Files Deleted
- `abis/hyperliquid_clearinghouse.json`
- `abis/hyperliquid_exchange.json`
- `abis/usdc.json`

## Getting Started with Lighter.xyz

### Prerequisites
1. **Lighter.xyz Account**: You need access to Lighter's private beta
2. **API Keys**: Generate API keys from your Lighter account
3. **Ethereum Wallet**: Your ETH wallet with private key

### Step 1: Get Lighter.xyz Credentials

#### 1.1 Generate API Key
- Log into your Lighter account
- Navigate to API settings
- Generate a new API key (use indices 2-254; 0 and 1 are reserved)
- Save the `API_KEY_PRIVATE_KEY`

#### 1.2 Get Your ETH Private Key
- Export your Ethereum wallet private key
- This is used to derive your Ethereum address for account identification
- **Keep this secure!**

#### 1.3 Find Your Account Index
You need to query the Lighter API to get your account index:

```python
import requests

# Your ETH address (derived from ETH_PRIVATE_KEY)
eth_address = "your_eth_address_here"

# Query Lighter API
response = requests.get(
    f"https://api.lighter.xyz/accountsByL1Address?address={eth_address}"
)

if response.status_code == 200:
    data = response.json()
    # First element in sub_accounts list is your main account
    account_index = data['sub_accounts'][0]
    print(f"Your account index: {account_index}")
```

Alternatively, check the [Lighter API documentation](https://apidocs.lighter.xyz/docs/account-index) for more details.

### Step 2: Install Lighter SDK

The Lighter SDK is not available on PyPI. You must clone it from GitHub:

```bash
# Clone the repository
git clone https://github.com/hangukquant/lighter_sdk

# Navigate to the SDK directory
cd lighter_sdk

# Install in editable mode
pip install -e .

# Return to your project directory
cd ..
```

### Step 3: Configure Environment

1. Copy `env_example.txt` to `.env`:
```bash
cp env_example.txt .env
```

2. Edit `.env` and fill in your Lighter.xyz credentials:
```env
# Lighter.xyz Configuration
LIGHTER_API_BASE=https://api.lighter.xyz
API_KEY_PRIVATE_KEY=your_api_key_private_key_here
ETH_PRIVATE_KEY=your_eth_private_key_here
LIGHTER_ACCOUNT_INDEX=your_account_index_here
API_KEY_INDEX=2

# Discord Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token

# Trading Configuration
MAX_POSITION_SIZE=0.1
LEVERAGE=2.0
AUTO_EXECUTE=false
```

### Step 4: Install Other Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Test Your Configuration

Run the test script to verify everything is set up correctly:

```bash
python test_config.py
```

### Step 6: Run in Simulation Mode First

Before going live, test the bot in simulation mode:

1. Leave `API_KEY_PRIVATE_KEY` or `ETH_PRIVATE_KEY` commented out in `.env`
2. Run the bot:
```bash
python discord_trader_bot.py
```
3. The bot will detect signals but won't execute trades
4. Check `discord_trader.log` for detected signals

### Step 7: Go Live

Once you're confident the bot is working correctly:

1. Uncomment and fill in all Lighter.xyz credentials in `.env`
2. Set `AUTO_EXECUTE=false` for manual confirmation mode (recommended)
3. Run the bot:
```bash
python discord_trader_bot.py
```
4. The bot will ask for confirmation before executing trades
5. React with ✅ to confirm or ❌ to ignore

## Key Differences: Hyperliquid vs Lighter.xyz

### Authentication
**Hyperliquid:**
```env
HL_API_PRIVATE_KEY=single_private_key
```

**Lighter.xyz:**
```env
API_KEY_PRIVATE_KEY=api_key_private_key
ETH_PRIVATE_KEY=eth_wallet_private_key
LIGHTER_ACCOUNT_INDEX=account_index
API_KEY_INDEX=2
```

### Order Placement
**Hyperliquid:**
```python
order = {
    "coin": symbol,
    "is_buy": True,
    "sz": position_size,
    "limit_px": execution_price,
    "order_type": {"limit": {"tif": "Gtc"}},
    "reduce_only": False
}
resp = self.exchange.place_order(order)
```

**Lighter.xyz:**
```python
nonce = self.transaction_api.next_nonce(self.account_index)
signed_order = self.signer_client.create_order(
    ticker=symbol,
    amount=str(position_size),
    price=str(execution_price),
    side='buy',
    order_type='limit'
)
resp = self.transaction_api.send_tx(signed_order)
```

### Market Data
**Hyperliquid:**
```python
response = requests.get(f"{self.api_base}/info")
```

**Lighter.xyz:**
```python
response = requests.get(f"{self.api_base}/markets/{symbol}")
```

## Trading Signal Formats

The bot still supports all the same trading signal formats:

### Single-Line Signals
```
BUY BTC AT 50000
SELL ETH @ 3000
SHORT SOL 150 5X
Market LONG BTC
```

### Multi-Line Signals
```
Limit Long BTC: 117320
Stop Loss: 116690
TP: 118900
```

### Laddered Entries
```
Long BTC
Entry: 50000 / 49500 / 49000
TP: 52000 / 54000 / 56000
Stop Loss: 48000
```

## Bot Commands

All Discord bot commands remain the same:

- `!status` - Check bot status and active trades
- `!toggle_auto` - Toggle auto-execution on/off
- `!close SYMBOL [PRICE]` - Close position (market if price omitted)

## Troubleshooting

### SDK Import Error
```
ModuleNotFoundError: No module named 'lighter'
```

**Solution:** Make sure you've cloned and installed the Lighter SDK:
```bash
git clone https://github.com/hangukquant/lighter_sdk
cd lighter_sdk
pip install -e .
```

### Account Index Error
```
Error: Could not determine account index
```

**Solution:** Query the `accountsByL1Address` endpoint with your ETH address to get your account index.

### Authentication Error
```
Error: Invalid API key or signature
```

**Solution:** 
- Verify your `API_KEY_PRIVATE_KEY` is correct
- Ensure your `ETH_PRIVATE_KEY` is correct
- Check that your `API_KEY_INDEX` matches the index you used when generating the API key
- Verify your `LIGHTER_ACCOUNT_INDEX` is correct

### Simulation Mode Warning
```
Simulation mode - signal tracked but not executed
```

**Solution:** This is expected behavior when credentials are not set. To enable live trading:
1. Set `API_KEY_PRIVATE_KEY` in `.env`
2. Set `ETH_PRIVATE_KEY` in `.env`
3. Set `LIGHTER_ACCOUNT_INDEX` in `.env`

## Additional Resources

- **Lighter API Documentation**: https://apidocs.lighter.xyz/docs/private-beta
- **Get Started for Programmers**: https://apidocs.lighter.xyz/docs/get-started-for-programmers-1
- **Account Index Guide**: https://apidocs.lighter.xyz/docs/account-index
- **Nonce Management**: https://apidocs.lighter.xyz/docs/nonce-management
- **Lighter SDK GitHub**: https://github.com/hangukquant/lighter_sdk
- **Discord Support**: Join Lighter's Discord (#api-updates channel)
- **Telegram API Channel**: For API updates and support

## Security Best Practices

1. **Never share your `.env` file**
2. **Keep your private keys secure**
3. **Start with simulation mode** to test signal detection
4. **Use manual confirmation mode** (`AUTO_EXECUTE=false`) initially
5. **Monitor logs regularly** in `discord_trader.log`
6. **Set reasonable position sizes** (e.g., `MAX_POSITION_SIZE=0.1` for 10%)
7. **Always use stop-loss levels** in your trading signals

## Support

If you encounter issues during migration:

1. Check the logs in `discord_trader.log` for detailed error messages
2. Review the [Lighter API documentation](https://apidocs.lighter.xyz/docs/private-beta)
3. Join Lighter's Discord community for support
4. Open an issue on this repository if you find bugs

## Migration Checklist

- [ ] Backed up old Hyperliquid configuration
- [ ] Generated Lighter.xyz API keys
- [ ] Found account index via API query
- [ ] Cloned and installed Lighter SDK
- [ ] Updated `.env` file with Lighter credentials
- [ ] Tested in simulation mode
- [ ] Verified signal detection works
- [ ] Tested with manual confirmation mode
- [ ] Ready for live trading!

---

**Note:** Lighter.xyz is currently in private beta. Make sure you have access before attempting to use this integration. API behavior may change as the platform evolves.

