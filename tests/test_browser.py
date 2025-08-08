"""Test script for browser tools functionality."""

import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_browser_imports():
    """Test that browser tool imports work correctly."""
    try:
        print("🧪 Testing Browser Tool Imports")
        print("=" * 40)
        
        # Test browser tools import
        from tools.browser import launch_browser, close_browser, get_browser_status
        print("✅ Browser tools imported successfully")
        
        # Test tools package import
        from tools import launch_browser as launch_from_package
        print("✅ Browser tools available from package")
        
        return True
        
    except Exception as e:
        print(f"❌ Browser import test failed: {e}")
        return False

def test_browser_tool_basic():
    """Test basic browser tool functionality without actually launching browser."""
    try:
        from tools.browser import launch_browser
        
        print("\n🧪 Testing Browser Tool Structure")
        print("=" * 40)
        
        # Check tool properties
        print(f"Tool name: {launch_browser.name}")
        print(f"Tool description: {launch_browser.description[:100]}...")
        print("✅ Browser tool structure looks correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Browser tool test failed: {e}")
        return False

def test_agent_integration():
    """Test that the agent can load with browser tools."""
    try:
        print("\n🧪 Testing Agent Integration")
        print("=" * 40)
        
        # Test that agent can be imported with browser tools
        from agent import LangChainAgent
        print("✅ Agent with browser tools can be imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent integration test failed: {e}")
        return False

def main():
    """Run all browser tests."""
    print("🚀 Browser Tool Tests")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_browser_imports()
    
    # Test tool structure
    tool_ok = test_browser_tool_basic()
    
    # Test agent integration
    agent_ok = test_agent_integration()
    
    print(f"\n📋 Test Summary:")
    print("=" * 20)
    print(f"Browser Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"Tool Structure: {'✅ PASS' if tool_ok else '❌ FAIL'}")
    print(f"Agent Integration: {'✅ PASS' if agent_ok else '❌ FAIL'}")
    
    if imports_ok and tool_ok and agent_ok:
        print("\n🎉 All browser tool tests passed!")
        print("\n📝 Ready to Use:")
        print("1. Make sure LM Studio is running with a model loaded")
        print("2. Run: python main.py")
        print("3. Try asking: 'Launch a browser and go to https://google.com'")
        print("\n⚠️  Browser Tool Notes:")
        print("- First browser launch may take a few seconds")
        print("- Screenshots are saved in the 'screenshots/' folder")
        print("- Use 'close browser' to clean up sessions")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
