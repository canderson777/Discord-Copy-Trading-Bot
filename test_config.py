#!/usr/bin/env python3
"""
Test script to validate environment configuration before running the bot
"""
import os
from dotenv import load_dotenv
from web3 import Web3

def test_environment():
    """Test environment variables and configuration"""
    print("🔍 Testing Copy Trader Bot Configuration...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Required variables for basic functionality
    required_vars = {
        'ARBITRUM_RPC_URL': 'Arbitrum RPC endpoint',
        'PRIVATE_KEY': 'Wallet private key',
        'DISCORD_BOT_TOKEN': 'Discord bot token',
    }
    
    # Optional variables
    optional_vars = {
        'CLEARINGHOUSE_ADDRESS': 'Hyperliquid clearinghouse contract',
        'EXCHANGE_ADDRESS': 'Hyperliquid exchange contract', 
        'USDC_ADDRESS': 'USDC token contract',
        'TRADING_CHANNEL_ID': 'Discord channel ID',
        'TRADER_USER_ID': 'Discord user ID to copy',
        'MAX_POSITION_SIZE': 'Maximum position size',
        'LEVERAGE': 'Trading leverage',
        'AUTO_EXECUTE': 'Auto-execute trades'
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
    
    # Test RPC connection
    print("\n🌐 NETWORK CONNECTION:")
    rpc_url = os.getenv('ARBITRUM_RPC_URL')
    if rpc_url:
        try:
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            if w3.is_connected():
                chain_id = w3.eth.chain_id
                print(f"  ✅ Connected to network (Chain ID: {chain_id})")
                if chain_id != 42161:
                    warnings.append(f"Chain ID {chain_id} is not Arbitrum (42161)")
            else:
                print(f"  ❌ Cannot connect to RPC")
                errors.append("RPC connection failed")
        except Exception as e:
            print(f"  ❌ RPC connection error: {str(e)}")
            errors.append("RPC connection failed")
    
    # Test wallet
    print("\n👛 WALLET:")
    private_key = os.getenv('PRIVATE_KEY')
    if private_key and rpc_url:
        try:
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            account = w3.eth.account.from_key(private_key)
            print(f"  ✅ Wallet address: {account.address}")
            
            # Check balance
            try:
                balance = w3.eth.get_balance(account.address)
                balance_eth = w3.from_wei(balance, 'ether')
                print(f"  💰 ETH balance: {balance_eth:.4f} ETH")
                if balance_eth < 0.01:
                    warnings.append("Low ETH balance for gas fees")
            except Exception as e:
                print(f"  ⚠️  Could not check balance: {str(e)}")
        except Exception as e:
            print(f"  ❌ Wallet error: {str(e)}")
            errors.append("Invalid private key")
    
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
