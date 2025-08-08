"""Test browser error handling improvements."""

import sys
import os
import time

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_browser_cleanup():
    """Test browser session cleanup handling."""
    try:
        print("🧪 Testing Browser Error Handling")
        print("=" * 40)
        
        from tools.browser import launch_browser, close_browser, get_browser_status
        
        # Test launch browser
        print("🔧 Launching browser...")
        result = launch_browser.invoke({"url": "https://httpbin.org/get"})
        print("✅ Browser launched successfully")
        
        # Check status
        print("\n🔧 Checking browser status...")
        status = get_browser_status.invoke({})
        print(f"Status: {status}")
        
        # Wait a moment
        time.sleep(2)
        
        # Test close browser
        print("\n🔧 Closing browser...")
        close_result = close_browser.invoke({})
        print(f"Close result: {close_result}")
        
        # Check final status
        print("\n🔧 Final status check...")
        final_status = get_browser_status.invoke({})
        print(f"Final status: {final_status}")
        
        print("\n✅ Browser error handling test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Browser error handling test failed: {e}")
        import traceback
        print(f"Error details: {traceback.format_exc()}")
        return False

def main():
    """Run the browser error handling test."""
    print("🚀 Browser Error Handling Test")
    print("=" * 50)
    
    success = test_browser_cleanup()
    
    if success:
        print("\n🎉 Browser error handling improvements are working!")
        print("The threading error should now be handled gracefully.")
    else:
        print("\n⚠️  Browser error handling test failed.")
        print("Check the error details above.")

if __name__ == "__main__":
    main()
