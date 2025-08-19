#!/usr/bin/env python3
"""
Test script to verify signal parsing works correctly
"""
import re

def parse_trade_message(message_content: str) -> dict:
    """Parse Discord message to extract trade signals - same logic as bot"""
    message = message_content.upper()
    
    # Common trading signal patterns
    patterns = [
        # Pattern 1: "BUY BTC AT 50000" or "SELL ETH @ 3000"
        r'(BUY|SELL|LONG|SHORT)\s+(\w+)\s+(?:AT|@)\s*\$?(\d+(?:\.\d+)?)',
        
        # Pattern 2: "BTC BUY 50000" or "ETH LONG $3000"
        r'(\w+)\s+(BUY|SELL|LONG|SHORT)\s*\$?(\d+(?:\.\d+)?)',
        
        # Pattern 3: "🚀 BTC LONG ENTRY: $50000"
        r'(?:🚀|📈|📊)?\s*(\w+)\s+(LONG|SHORT|BUY|SELL)\s+(?:ENTRY:?)?\s*\$?(\d+(?:\.\d+)?)',
        
        # Pattern 4: "SIGNAL: BUY BTC $50000"
        r'SIGNAL:?\s+(BUY|SELL|LONG|SHORT)\s+(\w+)\s*\$?(\d+(?:\.\d+)?)',
        
        # Pattern 5: "SHORT SOL 150" or "LONG BTC 50000"
        r'(LONG|SHORT)\s+(\w+)\s+(\d+(?:\.\d+)?)',
        
        # Pattern 6: "SELL ETHEREUM 3000"
        r'(BUY|SELL)\s+(\w+)\s+(\d+(?:\.\d+)?)',
        
        # Pattern 7: Handle "50k", "3k" etc.
        r'(BUY|SELL|LONG|SHORT)\s+(\w+)\s+(?:AT|@)?\s*\$?(\d+(?:\.\d+)?)[KkMm]?',
        
        # Pattern 8: "Position: LONG BTC ENTRY $50000"
        r'POSITION:?\s+(LONG|SHORT)\s+(\w+)\s+(?:ENTRY:?)?\s*\$?(\d+(?:\.\d+)?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message)
        if match:
            groups = match.groups()
            
            # Determine action and symbol based on pattern
            if len(groups) == 3:
                if groups[0] in ['BUY', 'SELL', 'LONG', 'SHORT']:
                    action, symbol, price = groups
                else:
                    symbol, action, price = groups
            else:
                continue
            
            # Normalize action
            if action in ['LONG', 'BUY']:
                action = 'BUY'
            elif action in ['SHORT', 'SELL']:
                action = 'SELL'
            
            # Handle price multipliers (K, M)
            if message.find(price + 'K') != -1:
                price = str(float(price) * 1000)
            elif message.find(price + 'M') != -1:
                price = str(float(price) * 1000000)
            
            # Extract leverage if mentioned
            leverage_match = re.search(r'(\d+)X|LEVERAGE[:\s]*(\d+)', message)
            leverage = '2.0'  # default
            if leverage_match:
                leverage = leverage_match.group(1) or leverage_match.group(2)
            
            return {
                'action': action,
                'symbol': symbol,
                'price': price,
                'leverage': leverage
            }
    
    return None

def test_signals():
    """Test various signal formats"""
    test_messages = [
        "BUY BTC AT 50000",
        "SELL ETH @ $3000", 
        "BTC LONG $45000",
        "🚀 ETH LONG ENTRY: $3200",
        "SIGNAL: BUY BTC $48000",
        "SHORT SOL 150 5X",
        "buy bitcoin at 50k",
        "LONG BTC 50000 2X",
        "📈 BITCOIN BUY $50000",
        "Invalid message",
        "SELL ETHEREUM 3000",
        "BTC TO THE MOON 🚀",
        "Position: LONG BTC ENTRY $50000",
    ]
    
    print("🧪 Testing Signal Parsing")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        result = parse_trade_message(message)
        status = "✅" if result else "❌"
        print(f"{i:2}. {status} '{message}'")
        if result:
            print(f"    → {result['action']} {result['symbol']} @ ${result['price']} (Leverage: {result['leverage']})")
        print()

if __name__ == "__main__":
    test_signals()
