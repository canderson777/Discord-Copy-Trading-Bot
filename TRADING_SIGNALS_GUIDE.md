# 🤖 Discord Copy Trader Bot - Complete Guide

## 🎮 Bot Commands

### Basic Commands
- `!status` - Check bot status, active trades, and trading mode
- `!ping` - Check bot connection and latency
- `!toggle_auto` - Toggle between manual confirmation and auto-execution
- `!close SYMBOL PRICE` - Manually close a position (e.g., `!close BTC 50000`)

### Example Usage
```
!status
!toggle_auto
!close BTC 117500
!ping
```

---

## 📊 Supported Signal Formats

### 🟢 Single-Line Signals

#### Basic Formats
```
BUY BTC AT 50000
SELL ETH @ 3000
LONG SOL 150
SHORT DOGE 0.08
```

#### With Symbols & Emojis
```
🚀 BTC LONG $50000
📈 ETH BUY 3200
💰 SOL LONG ENTRY: $150
📊 SHORT BTC $49000
```

#### Casual Formats
```
btc long 50k
eth buy $3000
Going long BTC at 50000
```

#### With Leverage
```
BTC LONG 50000 5X
SHORT ETH 3000 10X LEVERAGE
LONG SOL 150 2X
```

#### Signal Alerts
```
SIGNAL: BUY BTC $50000
Trade alert: LONG ETH 3200
Alert: SHORT SOL 150
```

---

### 🔥 Multi-Line Signals (Professional Format)

#### Standard Professional Format
```
Limit Long BTC: 117320
Stop Loss: 116690
TP: 118900
```

#### Market Orders
```
Market Buy ETH: 3200
Stop Loss: 3100
Take Profit: 3400
```

#### With Leverage
```
BTC LONG: 50000
STOP LOSS: 49000
TP: 52000
LEVERAGE: 5X
```

#### Short Positions
```
Short SOL: 150
Stop: 155
Target: 140
```

#### Alternative Formats
```
Entry: Long BTC 117320
SL: 116690
TP: 118900
```

```
BTC Position: LONG
Entry Price: 117320
Stop Loss: 116690
Take Profit: 118900
Risk: 2%
```

#### Advanced Multi-Line
```
📊 BTC Trade Setup
Limit Long BTC: 117320
Stop Loss: 116690
TP1: 118900
TP2: 120000
Leverage: 3X
Risk/Reward: 1:4
```

---

## 🎯 Signal Detection Rules

### ✅ What Gets Detected

1. **Action Words**: BUY, SELL, LONG, SHORT
2. **Symbols**: Any crypto symbol (BTC, ETH, SOL, etc.)
3. **Prices**: Numbers with optional $ sign, K/M multipliers
4. **Stop Loss**: "Stop Loss", "SL:", "Stop:"
5. **Take Profit**: "TP:", "Take Profit", "Target:"
6. **Leverage**: "5X", "LEVERAGE: 10", "10X LEVERAGE"

### ❌ What Gets Ignored

- Messages without clear action words
- Pure price discussions ("BTC is at 50k")
- Questions ("What do you think about ETH?")
- Hype messages ("🚀🚀🚀 TO THE MOON")

---

## 🔧 Bot Behavior

### Manual Mode (Default - Recommended)
```
1. Bot detects signal
2. Shows confirmation message with all details
3. Reacts with 🤔 (thinking)
4. Waits for your ✅ (execute) or ❌ (ignore) reaction
5. Executes trade if you confirm
```

### Auto Mode (Advanced Users)
```
1. Bot detects signal
2. Immediately executes trade
3. Reacts with ✅ (success) or ❌ (failed)
4. Posts confirmation message
```

---

## 💡 Pro Tips for Signal Recognition

### 🎯 Best Practices

1. **Use Clear Action Words**: "LONG", "SHORT", "BUY", "SELL"
2. **Include Symbol**: Always specify the crypto (BTC, ETH, etc.)
3. **Add Price**: Use numbers, $ optional
4. **Multi-line for Complex**: Use separate lines for SL/TP

### 📈 Examples from Real Traders

```
🔥 SIGNAL ALERT 🔥
LONG BTC: 117320
Stop Loss: 116690
Take Profit: 118900
Leverage: 3X
Risk Management: 2% account
```

```
Entry Setup:
Market Buy ETH 3200
SL: 3100
TP1: 3400
TP2: 3600
Size: 0.1 ETH
```

```
Quick Scalp:
SHORT SOL 150 5X
Stop: 152
Target: 145
```

---

## 🚨 Important Notes

### 🟡 Testing Mode (Current)
- Bot detects and logs all signals
- Shows ✅ reactions for successful detection
- **NO actual trades executed** (safe for testing)
- Perfect for learning the formats

### 🟢 Live Trading Mode (When Configured)
- Same detection + actual trade execution
- Requires Hyperliquid contract setup
- Real money at risk

### 🛡️ Safety Features
- Built-in stop-loss and take-profit from signals
- Position size limits
- Manual confirmation mode available
- Comprehensive logging

---

## 🔍 Troubleshooting

### Signal Not Detected?
1. Check action words (BUY/SELL/LONG/SHORT)
2. Ensure symbol is clear (BTC, ETH, etc.)
3. Include price in the message
4. Use `!status` to check bot connectivity

### Bot Not Responding?
1. Verify bot permissions in Discord
2. Check if you're the configured trader user
3. Ensure you're in the correct channel
4. Try `!ping` to test connection

---

## 📝 Configuration

### Required Settings
- `DISCORD_BOT_TOKEN` - Your Discord bot token
- `TRADING_CHANNEL_ID` - Channel to monitor (optional)
- `TRADER_USER_ID` - User to copy (optional)
- `AUTO_EXECUTE` - false (manual) or true (auto)

### Optional Settings
- `MAX_POSITION_SIZE` - Maximum position size
- `LEVERAGE` - Default leverage
- `STOP_LOSS_PERCENTAGE` - Default stop loss %
- `MIN_PROFIT_THRESHOLD` - Take profit threshold

---

**🎉 Your bot is sophisticated and ready for professional trading signals!**
