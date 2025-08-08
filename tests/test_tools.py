"""Test script for the weather tool functionality."""

import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_weather_tool():
    """Test the weather tool directly."""
    try:
        from tools.weather import get_weather
        
        print("🧪 Testing Weather Tool")
        print("=" * 30)
        
        # Test basic functionality
        print("Test 1: Basic weather query")
        result = get_weather.invoke({"location": "New York"})
        print(f"Result: {result}")
        print()
        
        # Test with fahrenheit
        print("Test 2: Weather with fahrenheit")
        result = get_weather.invoke({"location": "London", "unit": "fahrenheit"})
        print(f"Result: {result}")
        print()
        
        # Test with different location
        print("Test 3: Different location")
        result = get_weather.invoke({"location": "Tokyo, Japan"})
        print(f"Result: {result}")
        print()
        
        print("✅ All weather tool tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Weather tool test failed: {e}")
        return False

def test_agent_imports():
    """Test that all agent imports work correctly."""
    try:
        print("\n🧪 Testing Agent Imports")
        print("=" * 30)
        
        # Test config import
        from config import Config
        print("✅ Config imported successfully")
        
        # Test provider import
        from providers import LMStudioProvider
        print("✅ LMStudioProvider imported successfully")
        
        # Test tools import
        from tools import get_weather
        print("✅ Tools imported successfully")
        
        # Test agent import
        from agent import LangChainAgent
        print("✅ LangChainAgent imported successfully")
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 LangChain Agent Tool Tests")
    print("=" * 40)
    
    # Test imports first
    imports_ok = test_agent_imports()
    
    # Test weather tool
    weather_ok = test_weather_tool()
    
    print("\n📋 Test Summary:")
    print("=" * 20)
    print(f"Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"Weather Tool: {'✅ PASS' if weather_ok else '❌ FAIL'}")
    
    if imports_ok and weather_ok:
        print("\n🎉 All tests passed! Your agent is ready to use tools.")
        print("\n📝 Next Steps:")
        print("1. Make sure LM Studio is running with a model loaded")
        print("2. Start the local server in LM Studio")
        print("3. Run: python main.py")
        print("4. Try asking: 'What's the weather in Paris?'")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
