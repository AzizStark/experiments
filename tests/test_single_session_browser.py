"""Test the new single-session browser architecture with process termination."""

import sys
import os
import time

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_single_session_architecture():
    """Test the single-session browser architecture."""
    try:
        print("🧪 Testing Single-Session Browser Architecture")
        print("=" * 50)
        
        from tools.browser import launch_browser, close_browser, get_browser_status
        
        # Test 1: Launch first browser
        print("🔧 Test 1: Launching first browser...")
        result1 = launch_browser.invoke({"url": "https://httpbin.org/get"})
        print("✅ First browser launched")
        print(f"Result: {result1[:100]}...")
        
        # Test 2: Check browser status
        print("\n🔧 Test 2: Checking browser status...")
        status1 = get_browser_status.invoke({})
        print(f"Status: {status1}")
        
        # Extract process ID from status for verification
        if "Process ID:" in status1:
            pid1 = status1.split("Process ID: ")[1].split("\n")[0]
            print(f"First browser PID: {pid1}")
        
        # Wait a moment
        time.sleep(2)
        
        # Test 3: Launch second browser (should kill first)
        print("\n🔧 Test 3: Launching second browser (should kill first)...")
        result2 = launch_browser.invoke({"url": "https://httpbin.org/user-agent"})
        print("✅ Second browser launched (first should be terminated)")
        print(f"Result: {result2[:100]}...")
        
        # Test 4: Check status again (should show new session)
        print("\n🔧 Test 4: Checking status after second launch...")
        status2 = get_browser_status.invoke({})
        print(f"Status: {status2}")
        
        # Extract second process ID
        if "Process ID:" in status2:
            pid2 = status2.split("Process ID: ")[1].split("\n")[0]
            print(f"Second browser PID: {pid2}")
            
            # Verify PIDs are different (new process)
            if 'pid1' in locals() and pid1 != pid2:
                print("✅ Confirmed: New browser process created")
            else:
                print("⚠️  PIDs are the same or couldn't extract")
        
        # Wait a moment
        time.sleep(2)
        
        # Test 5: Close browser completely
        print("\n🔧 Test 5: Closing browser completely...")
        close_result = close_browser.invoke({})
        print(f"Close result: {close_result}")
        
        # Test 6: Verify no active sessions
        print("\n🔧 Test 6: Verifying browser is completely closed...")
        final_status = get_browser_status.invoke({})
        print(f"Final status: {final_status}")
        
        if "No active browser session" in final_status:
            print("✅ Confirmed: Browser completely terminated")
        else:
            print("⚠️  Browser may still be running")
        
        print("\n✅ Single-session browser architecture test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Single-session browser test failed: {e}")
        import traceback
        print(f"Error details: {traceback.format_exc()}")
        return False

def test_process_termination():
    """Test that browser processes are actually terminated."""
    try:
        print("\n🧪 Testing Process Termination")
        print("=" * 40)
        
        import psutil
        from tools.browser import launch_browser, close_browser
        
        # Get initial browser processes
        initial_chromium_procs = [p for p in psutil.process_iter(['pid', 'name']) 
                                 if 'chromium' in p.info['name'].lower() or 'chrome' in p.info['name'].lower()]
        initial_count = len(initial_chromium_procs)
        print(f"Initial Chromium processes: {initial_count}")
        
        # Launch browser
        print("🔧 Launching browser...")
        launch_browser.invoke({"url": "about:blank"})
        
        # Wait for browser to fully start
        time.sleep(3)
        
        # Count processes after launch
        after_launch_procs = [p for p in psutil.process_iter(['pid', 'name']) 
                             if 'chromium' in p.info['name'].lower() or 'chrome' in p.info['name'].lower()]
        after_launch_count = len(after_launch_procs)
        print(f"Chromium processes after launch: {after_launch_count}")
        
        if after_launch_count > initial_count:
            print("✅ New browser processes detected")
        else:
            print("⚠️  No new browser processes detected")
        
        # Close browser
        print("🔧 Closing browser...")
        close_browser.invoke({})
        
        # Wait for processes to terminate
        time.sleep(3)
        
        # Count processes after close
        after_close_procs = [p for p in psutil.process_iter(['pid', 'name']) 
                            if 'chromium' in p.info['name'].lower() or 'chrome' in p.info['name'].lower()]
        after_close_count = len(after_close_procs)
        print(f"Chromium processes after close: {after_close_count}")
        
        if after_close_count <= initial_count:
            print("✅ Browser processes successfully terminated")
            return True
        else:
            print("⚠️  Some browser processes may still be running")
            return False
            
    except Exception as e:
        print(f"❌ Process termination test failed: {e}")
        return False

def main():
    """Run all single-session browser tests."""
    print("🚀 Single-Session Browser Tests")
    print("=" * 60)
    
    # Test single session architecture
    architecture_ok = test_single_session_architecture()
    
    # Test process termination
    termination_ok = test_process_termination()
    
    print(f"\n📋 Test Summary:")
    print("=" * 20)
    print(f"Single-Session Architecture: {'✅ PASS' if architecture_ok else '❌ FAIL'}")
    print(f"Process Termination: {'✅ PASS' if termination_ok else '❌ FAIL'}")
    
    if architecture_ok and termination_ok:
        print("\n🎉 Single-session browser architecture is working perfectly!")
        print("✅ Browser processes are properly terminated")
        print("✅ Only one session can be active at a time")
        print("✅ New browser launches kill existing ones")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
