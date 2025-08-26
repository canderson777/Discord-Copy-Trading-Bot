#!/usr/bin/env python3
"""
Test script to validate environment configuration before running the bot
"""
import os
from dotenv import load_dotenv
from web3 import Web3
import requests

def test_environment():
    """Test environment variables and configuration"""
    print("🔍 Testing Copy Trader Bot Configuration...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Required variables for Discord functionality
    required_vars = {
        'DISCORD_BOT_TOKEN': 'Discord bot token',
    }
    
    # Optional variables
    optional_vars = {
        'TRADING_CHANNEL_ID': 'Discord channel ID',
        'TRADER_USER_ID': 'Discord user ID to copy',
        'MAX_POSITION_SIZE': 'Maximum position size (coin units)',
        'LEVERAGE': 'Trading leverage',
        'AUTO_EXECUTE': 'Auto-execute trades',
        'HYPERLIQUID_API_BASE': 'Hyperliquid API base URL',
        'HL_API_PRIVATE_KEY': 'Hyperliquid API wallet private key',
        'HL_TESTNET': 'Use Hyperliquid testnet endpoints'
    }
    
    errors = []
    warnings = []
    
    print("📋 REQUIRED CONFIGURATION:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            if var == 'PRIVATE_KEY':
                # Validate private key format
                pk = value
                if pk.startswith('0x'):
                    pk = pk[2:]
                
                if len(pk) == 64:
                    try:
                        int(pk, 16)
                        print(f"  ✅ {var}: Valid format")
                    except ValueError:
                        print(f"  ❌ {var}: Invalid hex format")
                        errors.append(f"{var} must be valid hexadecimal")
                else:
                    print(f"  ❌ {var}: Wrong length ({len(pk)} chars, need 64)")
                    errors.append(f"{var} must be 64 characters long")
            elif var == 'DISCORD_BOT_TOKEN':
                print(f"  ✅ {var}: Present")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: Missing - {description}")
            errors.append(f"Missing {var}")
    
    print("\n📋 OPTIONAL CONFIGURATION:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            if var in ['TRADING_CHANNEL_ID', 'TRADER_USER_ID']:
                try:
                    int(value)
                    print(f"  ✅ {var}: {value}")
                except ValueError:
                    print(f"  ⚠️  {var}: Invalid format (should be numeric)")
                    warnings.append(f"{var} should be a numeric Discord ID")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ⚠️  {var}: Not set - {description}")
            warnings.append(f"Consider setting {var}")
    
    # Test Hyperliquid API connectivity
    print("\n🌐 HYPERLIQUID API:")
    api_base = os.getenv('HYPERLIQUID_API_BASE', 'https://api.hyperliquid.xyz')
    try:
        r = requests.get(f"{api_base}/info", timeout=5)
        if r.status_code == 200:
            print(f"  ✅ API reachable at {api_base}")
        else:
            print(f"  ⚠️  API returned status {r.status_code} from {api_base}")
            warnings.append("Hyperliquid API returned non-200 status")
    except Exception as e:
        print(f"  ❌ API connection error: {str(e)}")
        warnings.append("Cannot reach Hyperliquid API base")
    
    # Test API mode credentials presence
    print("\n🔐 API MODE:")
    hl_pk = os.getenv('HL_API_PRIVATE_KEY')
    if hl_pk:
        masked = hl_pk[:6] + "..." + hl_pk[-4:] if len(hl_pk) > 12 else "(hidden)"
        print(f"  ✅ HL_API_PRIVATE_KEY: {masked}")
        print("  ✅ API mode credentials present")
    else:
        print("  ⚠️  HL_API_PRIVATE_KEY not set - running in simulation mode (no live trades)")
        warnings.append("API key not set; simulation mode only")
    
    # Summary
    print("\n" + "=" * 50)
    if errors:
        print("❌ CONFIGURATION ERRORS:")
        for error in errors:
            print(f"  • {error}")
        print("\n🔧 Fix these errors before running the bot!")
        return False
    elif warnings:
        print("✅ BASIC CONFIGURATION OK")
        print("⚠️  WARNINGS:")
        for warning in warnings:
            print(f"  • {warning}")
        print("\n✅ You can run the bot, but consider addressing warnings.")
        return True
    else:
        print("✅ ALL CONFIGURATION LOOKS GOOD!")
        print("🚀 Ready to run the bot!")
        return True

if __name__ == "__main__":
    success = test_environment()
    exit(0 if success else 1)
