#!/usr/bin/env python3
"""
Debug script to test market order regex patterns
"""
import re

def test_patterns():
    """Test the regex patterns for market orders"""
    print("🔍 Debugging Market Order Patterns")
    print("=" * 50)
    
    # Test commands
    test_commands = [
        "Buy Now ETH",
        "Buy Now BTC 30X", 
        "Market LONG",
        "Market SHORT",
        "buy now eth",
        "MARKET LONG",
    ]
    
    # The patterns from discord_trader_bot.py
    patterns = [
        # Pattern 1: "Buy Now ETH" or "Buy Now BTC 30X" (NEW - MOST SPECIFIC)
        r'BUY\s+NOW\s+(\w+)(?:\s+(\d+)X)?',
        
        # Pattern 2: "Market LONG" or "Market SHORT" (NEW)
        r'MARKET\s+(LONG|SHORT)',
        
        # Pattern 3: "Market Buy BTC 50000" or "Limit Sell ETH 3000"
        r'(MARKET|LIMIT)\s+(BUY|SELL|LONG|SHORT)\s+(\w+)\s+\$?(\d+(?:\.\d+)?)',
        
        # Pattern 4: "🚀 Market Long BTC $50000" or "📈 Limit Short ETH 3000"
        r'(?:🚀|📈|📊)?\s*(MARKET|LIMIT)\s+(LONG|SHORT|BUY|SELL)\s+(\w+)\s+\$?(\d+(?:\.\d+)?)',
        
        # Pattern 5: "SIGNAL: BUY BTC $50000"
        r'SIGNAL:?\s+(BUY|SELL|LONG|SHORT)\s+(\w+)\s*\$?(\d+(?:\.\d+)?)',
        
        # Pattern 6: "Position: LONG BTC ENTRY $50000"
        r'POSITION:?\s+(LONG|SHORT)\s+(\w+)\s+(?:ENTRY:?)?\s*\$?(\d+(?:\.\d+)?)',
        
        # Pattern 7: "BUY BTC AT 50000" or "SELL ETH @ 3000"
        r'(BUY|SELL|LONG|SHORT)\s+(\w+)\s+(?:AT|@)\s*\$?(\d+(?:\.\d+)?)',
        
        # Pattern 8: "BTC BUY 50000" or "ETH LONG $3000"  
        r'(\w+)\s+(BUY|SELL|LONG|SHORT)\s+\$?(\d+(?:\.\d+)?)',
        
        # Pattern 9: "🚀 BTC LONG ENTRY: $50000"
        r'(?:🚀|📈|📊)?\s*(\w+)\s+(LONG|SHORT|BUY|SELL)\s+(?:ENTRY:?)?\s*\$?(\d+(?:\.\d+)?)',
        
        # Pattern 10: "SHORT SOL 150" or "LONG BTC 50000"
        r'(LONG|SHORT)\s+(\w+)\s+(\d+(?:\.\d+)?)',
        
        # Pattern 11: "SELL ETHEREUM 3000"
        r'(BUY|SELL)\s+(\w+)\s+(\d+(?:\.\d+)?)',
        
        # Pattern 12: Handle "50k", "3k" etc. (LEAST SPECIFIC)
        r'(BUY|SELL|LONG|SHORT)\s+(\w+)\s+(?:AT|@)?\s*\$?(\d+(?:\.\d+)?)[KkMm]?',
    ]
    
    for command in test_commands:
        print(f"\n📝 Testing: '{command}'")
        message = command.upper()
        
        for i, pattern in enumerate(patterns, 1):
            match = re.search(pattern, message)
            if match:
                groups = match.groups()
                print(f"   ✅ Pattern {i} matched: {groups}")
                
                # Determine what this pattern should produce
                if i == 1:  # Buy Now pattern
                    if len(groups) == 2 and groups[1] and groups[1].isdigit():
                        print(f"   📋 Should be: BUY {groups[0]} at market price, leverage {groups[1]}X")
                    else:
                        print(f"   📋 Should be: BUY {groups[0]} at market price, default leverage")
                elif i == 2:  # Market LONG/SHORT pattern
                    print(f"   📋 Should be: {groups[0]} BTC at market price")
                else:
                    print(f"   📋 General pattern match")
                break
        else:
            print(f"   ❌ No pattern matched")

if __name__ == "__main__":
    test_patterns()
