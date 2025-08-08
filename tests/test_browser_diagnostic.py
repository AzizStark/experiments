"""Diagnostic script to identify browser launching issues."""

import sys
import os
import traceback

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_patchright_import():
    """Test if Patchright can be imported."""
    try:
        from patchright.sync_api import sync_playwright
        print("✅ Patchright imported successfully")
        return True, sync_playwright
    except ImportError as e:
        print(f"❌ Failed to import Patchright: {e}")
        return False, None
    except Exception as e:
        print(f"❌ Unexpected error importing Patchright: {e}")
        return False, None

def test_playwright_start():
    """Test if Playwright can start."""
    try:
        from patchright.sync_api import sync_playwright
        playwright = sync_playwright().start()
        print("✅ Playwright started successfully")
        playwright.stop()
        return True
    except Exception as e:
        print(f"❌ Failed to start Playwright: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return False

def test_browser_launch_basic():
    """Test basic browser launch."""
    try:
        from patchright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            print("🔧 Attempting to launch Chromium...")
            browser = p.chromium.launch(headless=True)
            print("✅ Browser launched successfully (headless)")
            browser.close()
            print("✅ Browser closed successfully")
            return True
    except Exception as e:
        print(f"❌ Failed to launch browser: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return False

def test_browser_launch_visible():
    """Test visible browser launch."""
    try:
        from patchright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            print("🔧 Attempting to launch visible browser...")
            browser = p.chromium.launch(headless=False)
            print("✅ Visible browser launched successfully")
            
            # Try to create a page
            page = browser.new_page()
            print("✅ New page created successfully")
            
            # Close everything
            page.close()
            browser.close()
            print("✅ Browser resources cleaned up")
            return True
    except Exception as e:
        print(f"❌ Failed to launch visible browser: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return False

def test_browser_with_navigation():
    """Test browser with navigation."""
    try:
        from patchright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            print("🔧 Testing browser with navigation...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Try to navigate to a simple page
            response = page.goto("https://httpbin.org/get", timeout=10000)
            print(f"✅ Navigation successful: {response.status}")
            
            browser.close()
            return True
    except Exception as e:
        print(f"❌ Failed browser navigation test: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return False

def test_chromium_executable():
    """Test if Chromium executable exists."""
    try:
        from patchright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            executable_path = p.chromium.executable_path
            print(f"🔧 Chromium executable path: {executable_path}")
            
            if os.path.exists(executable_path):
                print("✅ Chromium executable found")
                return True
            else:
                print("❌ Chromium executable not found")
                print("💡 Try running: patchright install chromium")
                return False
    except Exception as e:
        print(f"❌ Failed to check Chromium executable: {e}")
        return False

def main():
    """Run all diagnostic tests."""
    print("🚀 Browser Launch Diagnostic")
    print("=" * 50)
    
    tests = [
        ("Patchright Import", test_patchright_import),
        ("Playwright Start", test_playwright_start),
        ("Chromium Executable", test_chromium_executable),
        ("Basic Browser Launch", test_browser_launch_basic),
        ("Visible Browser Launch", test_browser_launch_visible),
        ("Browser Navigation", test_browser_with_navigation),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 30)
        
        if test_name == "Patchright Import":
            success, _ = test_func()
            results[test_name] = success
        else:
            results[test_name] = test_func()
    
    # Summary
    print(f"\n📋 Diagnostic Summary:")
    print("=" * 30)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    print("=" * 20)
    
    if not results.get("Patchright Import", False):
        print("1. Install Patchright: pip install patchright")
    
    if not results.get("Chromium Executable", False):
        print("2. Install Chromium: patchright install chromium")
    
    if not results.get("Basic Browser Launch", False):
        print("3. Check system dependencies:")
        print("   - macOS: brew install --cask chromium")
        print("   - Ubuntu: sudo apt-get install chromium-browser")
    
    if not results.get("Visible Browser Launch", False):
        print("4. Display issues - try headless mode first")
    
    if all(results.values()):
        print("🎉 All tests passed! Browser should work correctly.")
    else:
        print("⚠️  Some tests failed. Address the issues above.")

if __name__ == "__main__":
    main()
