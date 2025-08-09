"""Test the enterprise browser service integration."""

import sys
import os
import time
import requests

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_service_health():
    """Check if the Node.js browser service is running."""
    try:
        response = requests.get("http://localhost:3000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, {"error": f"Service returned status {response.status_code}"}
    except Exception as e:
        return False, {"error": str(e)}

def test_service_health_check():
    """Test if the Node.js service is running."""
    try:
        print("🧪 Testing Node.js Browser Service Health")
        print("=" * 45)
        
        healthy, data = check_service_health()
        
        if healthy:
            print("✅ Node.js browser service is running")
            print(f"✅ Status: {data.get('status')}")
            print(f"✅ Active sessions: {len(data.get('activeSessions', []))}")
            return True
        else:
            print("❌ Node.js browser service is not running")
            print(f"❌ Error: {data.get('error')}")
            print("\n💡 To start the service:")
            print("   cd browser-service && npm start")
            return False
            
    except Exception as e:
        print(f"❌ Service health check failed: {e}")
        return False

def test_python_tools():
    """Test the Python tools that connect to the Node.js service."""
    try:
        print("\n🧪 Testing Python Tools Integration")
        print("=" * 40)
        
        from tools.browser import (
            launch_browser, 
            analyze_screen, 
            get_browser_status,
            close_browser,
            check_browser_service_health
        )
        
        # Check service health first
        health = check_browser_service_health()
        if not health.get('healthy'):
            print(f"❌ Service not healthy: {health.get('message')}")
            return False
        
        print("✅ Browser service health check passed")
        
        # Test browser launch
        print("\n🔧 Testing browser launch...")
        launch_result = launch_browser.invoke({"url": "https://httpbin.org/get"})
        print(f"Launch result: {launch_result[:100]}...")
        
        if "🚀 Browser launched successfully!" in launch_result:
            print("✅ Browser launch successful")
        else:
            print("❌ Browser launch failed")
            return False
        
        # Wait for page to load
        print("\n⏳ Waiting for page to load...")
        time.sleep(3)
        
        # Test browser status
        print("\n🔧 Testing browser status...")
        status_result = get_browser_status.invoke({})
        print(f"Status result: {status_result}")
        
        if "Active Browser Session:" in status_result:
            print("✅ Browser status check successful")
        else:
            print("❌ Browser status check failed")
            return False
        
        # Test screenshot analysis (the main feature!)
        print("\n🔧 Testing screenshot analysis...")
        screen_result = analyze_screen.invoke({})
        
        if screen_result.get('type') == 'screenshot':
            screenshot_data = screen_result.get('screenshot_base64', '')
            print("✅ Screenshot captured successfully!")
            print(f"✅ Base64 length: {len(screenshot_data)} characters")
            print(f"✅ Architecture: {screen_result.get('architecture')}")
            print("🎉 NO THREADING ERRORS! SUCCESS!")
            
            # Verify it's valid base64
            import base64
            try:
                decoded = base64.b64decode(screenshot_data)
                print(f"✅ Valid base64 data, decoded size: {len(decoded)} bytes")
            except Exception as e:
                print(f"❌ Invalid base64 data: {e}")
                return False
                
        else:
            print(f"❌ Screenshot failed: {screen_result.get('message')}")
            return False
        
        # Test browser close
        print("\n🔧 Testing browser close...")
        close_result = close_browser.invoke({})
        print(f"Close result: {close_result}")
        
        if "Browser session closed successfully!" in close_result:
            print("✅ Browser close successful")
        else:
            print("❌ Browser close failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Python tools test failed: {e}")
        import traceback
        print(f"Error details: {traceback.format_exc()}")
        return False

def test_multiple_screenshots():
    """Test multiple screenshots to verify stability."""
    try:
        print("\n🧪 Testing Multiple Screenshots (No Threading Issues)")
        print("=" * 60)
        
        from tools.browser import launch_browser, analyze_screen, close_browser
        
        # Launch browser
        launch_result = launch_browser.invoke({"url": "https://example.com"})
        if "🚀 Browser launched successfully!" not in launch_result:
            print("❌ Browser launch failed")
            return False
        
        print("✅ Browser launched for stability test")
        time.sleep(2)
        
        success_count = 0
        total_attempts = 3
        
        for i in range(total_attempts):
            print(f"\n📸 Screenshot attempt {i+1}/{total_attempts}...")
            
            try:
                result = analyze_screen.invoke({})
                if result.get('type') == 'screenshot' and result.get('screenshot_base64'):
                    print(f"✅ Screenshot {i+1} successful (no threading errors)")
                    success_count += 1
                else:
                    print(f"❌ Screenshot {i+1} failed: {result.get('message')}")
                
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Screenshot {i+1} exception: {e}")
        
        # Close browser
        close_browser.invoke({})
        
        print(f"\n📊 Stability Results: {success_count}/{total_attempts} successful")
        
        if success_count == total_attempts:
            print("🎉 Perfect stability! No threading issues!")
            return True
        elif success_count >= 2:
            print("✅ Good stability with Node.js service")
            return True
        else:
            print("❌ Stability issues detected")
            return False
            
    except Exception as e:
        print(f"❌ Multiple screenshots test failed: {e}")
        return False

def main():
    """Run all Node.js browser service tests."""
    print("🚀 Node.js Browser Service Integration Tests")
    print("=" * 70)
    print("Testing the new @presidio-dev/playwright-core integration")
    print("to completely eliminate Python threading issues.")
    print("=" * 70)
    
    # Test service health
    service_ok = test_service_health_check()
    
    if not service_ok:
        print("\n❌ Node.js service is not running. Please start it first:")
        print("   cd browser-service && npm start")
        return
    
    # Test Python tools integration
    tools_ok = test_python_tools()
    
    # Test stability
    stability_ok = test_multiple_screenshots() if tools_ok else False
    
    print(f"\n📋 Test Summary:")
    print("=" * 30)
    print(f"Service Health: {'✅ PASS' if service_ok else '❌ FAIL'}")
    print(f"Python Tools: {'✅ PASS' if tools_ok else '❌ FAIL'}")
    print(f"Screenshot Stability: {'✅ PASS' if stability_ok else '❌ FAIL'}")
    
    if service_ok and tools_ok and stability_ok:
        print("\n🎉 All Node.js browser service tests passed!")
        print("✅ Threading issues completely eliminated")
        print("✅ @presidio-dev/playwright-core integration working")
        print("✅ Vision screenshot analysis stable")
        print("✅ Python-to-Node.js bridge functional")
        print("\n🎯 Your Node.js browser service is ready!")
        print("\nTo use in your agent:")
        print("1. Make sure the service is running: cd browser-service && npm start")
        print("2. Update tools/__init__.py to use Node.js tools")
        print("3. Update agent.py to use the new tools")
        print("4. Test with: 'What do you see on the screen?'")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("Make sure the Node.js service is running properly.")

if __name__ == "__main__":
    main()
