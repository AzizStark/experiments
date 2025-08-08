"""Direct test of the browser tool after fixing the Chrome channel issue."""

import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_browser_tool_direct():
    """Test the browser tool directly."""
    try:
        print("🧪 Testing Browser Tool Directly")
        print("=" * 40)
        
        from tools.browser import launch_browser, close_browser, get_browser_status
        
        print("✅ Browser tools imported successfully")
        
        # Test launch browser tool
        print("\n🔧 Testing launch_browser tool...")
        result = launch_browser.invoke({"url": "https://httpbin.org/get"})
        print(f"Launch result: {result}")
        
        # Test browser status
        print("\n🔧 Testing get_browser_status tool...")
        status = get_browser_status.invoke({})
        print(f"Status result: {status}")
        
        # Test close browser
        print("\n🔧 Testing close_browser tool...")
        close_result = close_browser.invoke({})
        print(f"Close result: {close_result}")
        
        print("\n✅ All browser tool tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Browser tool test failed: {e}")
        import traceback
        print(f"Error details: {traceback.format_exc()}")
        return False

def main():
    """Run the direct browser tool test."""
    print("🚀 Direct Browser Tool Test")
    print("=" * 50)
    
    success = test_browser_tool_direct()
    
    if success:
        print("\n🎉 Browser tool is working correctly!")
        print("You can now use it in your agent.")
    else:
        print("\n⚠️  Browser tool test failed.")
        print("Check the error details above.")

if __name__ == "__main__":
    main()
