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



--------------------------------------------------------------------------------------------------



# 📚 GitHub Repository Setup Guide

Follow these steps to create a new GitHub repository for your Discord Copy Trader Bot.

## 🚀 Step 1: Create GitHub Repository

### Option A: Via GitHub Website (Recommended)
1. Go to [GitHub.com](https://github.com) and log in
2. Click the **"+"** icon in the top right corner
3. Select **"New repository"**
4. Fill in the details:
   - **Repository name**: `discord-copy-trader-bot`
   - **Description**: `Advanced Discord bot for copy trading cryptocurrency signals`
   - **Visibility**: Choose **Public** or **Private**
   - ✅ Check **"Add a README file"** (we'll overwrite it)
   - ✅ Check **"Add .gitignore"** → Select **"Python"**
   - ✅ Check **"Choose a license"** → Select **"MIT License"**
5. Click **"Create repository"**

### Option B: Via GitHub CLI (Advanced)
```bash
# Install GitHub CLI first: https://cli.github.com/
gh repo create discord-copy-trader-bot --public --description "Advanced Discord bot for copy trading cryptocurrency signals"
```

## 📁 Step 2: Prepare Your Local Repository

### Initialize Git (if not already done)
```bash
cd "C:\Users\Jay\Documents\Copy Trader Bot"
git init
```

### Add Remote Repository
```bash
# Replace YOUR_USERNAME with your actual GitHub username
git remote add origin https://github.com/YOUR_USERNAME/discord-copy-trader-bot.git
```

### Configure Git (if first time)
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

## 📋 Step 3: Stage Your Files

### Add All Files
```bash
git add .
```

### Check What Will Be Committed
```bash
git status
```

You should see files like:
- ✅ `copy_trader.py`
- ✅ `discord_trader_bot.py`
- ✅ `requirements.txt`
- ✅ `README.md`
- ✅ `.gitignore`
- ✅ `LICENSE`
- ❌ `.env` (should be ignored)

## 💾 Step 4: Commit Your Code

```bash
git commit -m "Initial commit: Discord Copy Trader Bot

- Advanced signal detection for single and multi-line formats
- Support for professional trading signals with SL/TP
- Safe testing mode with manual confirmation
- Comprehensive logging and error handling
- Ready for Hyperliquid integration"
```

## 🚀 Step 5: Push to GitHub

### First Push
```bash
git branch -M main
git push -u origin main
```

### Future Pushes (after making changes)
```bash
git add .
git commit -m "Your commit message here"
git push
```

## 🔧 Step 6: Repository Settings (Optional)

### Enable Issues and Discussions
1. Go to your repository on GitHub
2. Click **"Settings"** tab
3. Scroll to **"Features"** section
4. ✅ Enable **"Issues"**
5. ✅ Enable **"Discussions"**

### Add Repository Topics
1. Click the **⚙️** gear icon next to "About"
2. Add topics: `discord-bot`, `crypto-trading`, `copy-trading`, `python`, `cryptocurrency`

### Create Repository Badges
Add these to your README.md:
```markdown
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Discord](https://img.shields.io/badge/Discord-Bot-7289da.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
```

## 📚 Step 7: Create Additional Branches (Optional)

### Development Branch
```bash
git checkout -b development
git push -u origin development
```

### Feature Branches
```bash
git checkout -b feature/new-signal-format
# Make your changes
git add .
git commit -m "Add support for new signal format"
git push -u origin feature/new-signal-format
```

## 🛡️ Step 8: Security Setup

### Add Branch Protection
1. Go to **Settings** → **Branches**
2. Click **"Add rule"**
3. Branch name pattern: `main`
4. ✅ **"Require pull request reviews"**
5. ✅ **"Dismiss stale reviews"**

### Add Secrets (for CI/CD later)
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add secrets like:
   - `DISCORD_BOT_TOKEN`
   - `PRIVATE_KEY`
   - etc.

## 📝 Step 9: Create Issues and Milestones

### Sample Issues
1. **"Add support for Binance signals"**
2. **"Create web dashboard"**
3. **"Improve error handling"**
4. **"Add unit tests"**

### Milestones
1. **v1.0 - Basic Discord Integration**
2. **v1.1 - Advanced Signal Parsing**
3. **v2.0 - Live Trading Integration**

## 🎯 Step 10: Share Your Repository

### Update README with Your Details
```bash
# Edit README.md to include:
# - Your GitHub username in clone command
# - Your Discord server link (if any)
# - Your contribution guidelines
```

### Create a Release
1. Go to **"Releases"** on GitHub
2. Click **"Create a new release"**
3. Tag: `v1.0.0`
4. Title: `Discord Copy Trader Bot v1.0.0`
5. Description: List features and setup instructions

## ✅ Verification Checklist

- [ ] Repository created on GitHub
- [ ] Local code pushed successfully
- [ ] README.md displays properly
- [ ] .gitignore working (no .env file in repo)
- [ ] License file present
- [ ] All Python files included
- [ ] Requirements.txt updated
- [ ] Repository topics added
- [ ] Branch protection enabled (optional)

## 🚨 Important Security Notes

### Never Commit These Files:
- ❌ `.env` files
- ❌ Private keys
- ❌ API tokens
- ❌ Personal Discord IDs (use placeholders)

### Safe to Commit:
- ✅ `env_example.txt` (template)
- ✅ All `.py` files
- ✅ Documentation
- ✅ Requirements and configuration templates

## 🎉 You're Done!

Your Discord Copy Trader Bot is now live on GitHub! 

**Next steps:**
1. Share the repository link with others
2. Set up GitHub Pages for documentation (optional)
3. Add continuous integration with GitHub Actions
4. Create a project board for tracking development

**Repository URL:** `https://github.com/YOUR_USERNAME/discord-copy-trader-bot`
