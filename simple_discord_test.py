#!/usr/bin/env python3
"""
Simple Discord connection test
"""
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} has connected to Discord!')
    print(f'🤖 Bot is in {len(bot.guilds)} servers')
    for guild in bot.guilds:
        print(f'   - {guild.name} (ID: {guild.id})')

@bot.event 
async def on_message(message):
    # Don't respond to bot messages
    if message.author.bot:
        return
    
    print(f"📨 Message from {message.author.display_name} in #{message.channel.name}: {message.content}")
    
    # Test simple signal detection
    if any(word in message.content.upper() for word in ['BUY', 'SELL', 'LONG', 'SHORT']):
        print(f"🎯 Potential signal detected!")
        await message.add_reaction('👀')
    
    # Process commands
    await bot.process_commands(message)

@bot.command(name='test')
async def test_command(ctx):
    """Test command to verify bot is working"""
    await ctx.send('🤖 Bot is working! Ready to detect signals.')

@bot.command(name='ping')
async def ping_command(ctx):
    """Ping command"""
    await ctx.send(f'🏓 Pong! Latency: {round(bot.latency * 1000)}ms')

def main():
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("❌ Discord bot token not found!")
        return
    
    print("🚀 Starting simple Discord test bot...")
    print("📝 Commands: !test, !ping")
    print("🎯 Will react to messages containing: BUY, SELL, LONG, SHORT")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        bot.run(token)
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
