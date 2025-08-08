"""Setup script for LangChain Agent."""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Main setup function."""
    print("🚀 LangChain Agent Setup")
    print("=" * 30)
    
    # Required packages
    packages = [
        "langchain>=0.1.0",
        "langchain-openai>=0.1.0", 
        "langchain-community>=0.0.20",
        "python-dotenv>=1.0.0"
    ]
    
    print("Installing required packages...")
    
    failed_packages = []
    for package in packages:
        print(f"Installing {package}...")
        if install_package(package):
            print(f"✅ {package} installed successfully")
        else:
            print(f"❌ Failed to install {package}")
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n⚠️  Some packages failed to install: {failed_packages}")
        print("Please install them manually:")
        for package in failed_packages:
            print(f"  pip install {package}")
    else:
        print("\n✅ All packages installed successfully!")
    
    print("\n📋 Next Steps:")
    print("1. Set up LM Studio:")
    print("   - Download from https://lmstudio.ai")
    print("   - Download and load a model")
    print("   - Start the local server")
    print("2. Run the agent:")
    print("   python main.py")
    
    print("\n🎉 Setup complete!")

if __name__ == "__main__":
    main()
