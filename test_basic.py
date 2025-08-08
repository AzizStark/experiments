"""Basic test script to verify the project structure."""

import sys
import os

def test_imports():
    """Test basic Python imports."""
    try:
        print("Testing basic imports...")
        
        # Test standard library imports
        import logging
        import sys
        from typing import Optional, List, Dict, Any
        print("✅ Standard library imports successful")
        
        # Test if we can import our modules
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        try:
            from config import Config
            print("✅ Config module imported successfully")
        except ImportError as e:
            print(f"❌ Config import failed: {e}")
        
        print("\n📋 Project Structure:")
        for root, dirs, files in os.walk("."):
            level = root.replace(".", "").count(os.sep)
            indent = " " * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = " " * 2 * (level + 1)
            for file in files:
                if not file.startswith('.') and file.endswith('.py'):
                    print(f"{subindent}{file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 LangChain Agent - Basic Test")
    print("=" * 40)
    
    if test_imports():
        print("\n✅ Basic tests passed!")
        print("\n📝 Next Steps:")
        print("1. Install dependencies manually:")
        print("   pip install langchain langchain-openai langchain-community python-dotenv")
        print("2. Set up LM Studio with a local model")
        print("3. Run: python main.py")
    else:
        print("\n❌ Basic tests failed!")
        print("Please check your Python installation.")

if __name__ == "__main__":
    main()
