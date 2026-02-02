#!/usr/bin/env python3

print("Script starting...")

try:
    import asyncio
    print("asyncio imported")
    
    from commonMethods import BrowserOperations
    print("BrowserOperations imported")
    
    from browser_agent import BrowserAgent
    print("BrowserAgent imported")
    
    print("Creating agent...")
    agent = BrowserAgent()
    print("Agent created")
    
    print("Loading test data...")
    test_params = agent.load_test_data()
    print(f"Test params: {test_params}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("Script completed")
