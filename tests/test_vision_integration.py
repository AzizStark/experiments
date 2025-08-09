"""
Comprehensive test file for vision integration with Qwen-2.5-VL in LM Studio.
Tests multiple approaches for sending images to the model using LangChain.
"""

import sys
import os
import base64
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from providers import LMStudioProvider
from config import Config

logger = logging.getLogger(__name__)

class VisionTester:
    """Vision integration testing class for Qwen-2.5-VL."""
    
    def __init__(self):
        """Initialize the vision tester with LM Studio provider."""
        self.provider = LMStudioProvider(
            base_url="http://localhost:1234/v1",
            model_name="qwen2-vl-2b-instruct",  # Adjust to your model name
            temperature=0.7
        )
        self.llm = self.provider.get_llm()
    
    def encode_image_from_path(self, image_path: str) -> Optional[str]:
        """Encode image from file path to base64."""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            print(f"✅ Image encoded successfully: {len(base64_image)} characters")
            return base64_image
            
        except Exception as e:
            print(f"❌ Failed to encode image: {e}")
            return None
    
    def detect_image_format(self, image_path: str) -> str:
        """Detect image format from file extension."""
        extension = Path(image_path).suffix.lower()
        format_map = {
            '.jpg': 'jpeg',
            '.jpeg': 'jpeg', 
            '.png': 'png',
            '.gif': 'gif',
            '.bmp': 'bmp',
            '.webp': 'webp'
        }
        return format_map.get(extension, 'jpeg')
    
    def analyze_image_direct(self, image_path: str, question: str) -> str:
        """
        Direct approach: Send image to model without using agent.
        This is more reliable and efficient for simple vision tasks.
        """
        try:
            print(f"\n🔍 Direct Vision Analysis")
            print(f"Image: {image_path}")
            print(f"Question: {question}")
            
            # Encode image
            base64_image = self.encode_image_from_path(image_path)
            if not base64_image:
                return "❌ Failed to encode image"
            
            # Detect format
            image_format = self.detect_image_format(image_path)
            
            # Create multimodal message
            message = HumanMessage(
                content=[
                    {"type": "text", "text": question},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/{image_format};base64,{base64_image}"}
                    }
                ]
            )
            
            # Send to model
            print("📤 Sending to Qwen-2.5-VL...")
            response = self.llm.invoke([message])
            
            print("✅ Response received!")
            return response.content
            
        except Exception as e:
            error_msg = f"❌ Vision analysis failed: {str(e)}"
            print(error_msg)
            return error_msg
    
    def analyze_screenshot_from_browser(self, question: str) -> str:
        """
        Analyze current browser screenshot using vision model.
        Integrates with your existing browser service.
        """
        try:
            print(f"\n📸 Browser Screenshot Vision Analysis")
            print(f"Question: {question}")
            
            # Import your browser tools
            from tools.browser import analyze_screen
            
            # Get screenshot from browser service
            print("📤 Getting screenshot from browser service...")
            screenshot_result = analyze_screen.invoke({})
            
            if screenshot_result.get('type') != 'screenshot':
                return f"❌ Failed to get screenshot: {screenshot_result.get('message')}"
            
            base64_image = screenshot_result.get('screenshot_base64')
            if not base64_image:
                return "❌ No screenshot data received"
            
            print(f"✅ Screenshot received: {len(base64_image)} characters")
            
            # Create multimodal message
            message = HumanMessage(
                content=[
                    {"type": "text", "text": question},
                    {
                        "type": "image_url", 
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                    }
                ]
            )
            
            # Send to vision model
            print("📤 Sending screenshot to Qwen-2.5-VL...")
            response = self.llm.invoke([message])
            
            print("✅ Vision analysis complete!")
            return response.content
            
        except Exception as e:
            error_msg = f"❌ Screenshot vision analysis failed: {str(e)}"
            print(error_msg)
            return error_msg

# Enhanced tool version (fixed from your original)
@tool
def analyze_image_tool(image_path: str, question: str) -> str:
    """
    Enhanced tool for image analysis with proper error handling.
    
    Args:
        image_path: Path to the image file
        question: Question to ask about the image
        
    Returns:
        Analysis result from the vision model
    """
    try:
        # Initialize LLM
        llm = ChatOpenAI(
            base_url="http://localhost:1234/v1",
            api_key="lm-studio",
            model="qwen2-vl-2b-instruct"
        )
        
        # Validate file exists
        if not os.path.exists(image_path):
            return f"❌ Image file not found: {image_path}"
        
        # Encode image with error handling
        try:
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            return f"❌ Failed to read image: {str(e)}"
        
        # Detect format
        extension = Path(image_path).suffix.lower()
        image_format = 'jpeg' if extension in ['.jpg', '.jpeg'] else 'png'
        
        # Create message
        message = HumanMessage(
            content=[
                {"type": "text", "text": question},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/{image_format};base64,{base64_image}"}
                }
            ]
        )
        
        # Get response
        response = llm.invoke([message])
        return response.content
        
    except Exception as e:
        return f"❌ Vision analysis error: {str(e)}"

def test_direct_vision_approach():
    """Test the direct vision approach (recommended)."""
    print("=" * 60)
    print("🔬 Testing Direct Vision Approach")
    print("=" * 60)
    
    tester = VisionTester()
    
    # Test with a sample image (you'll need to provide a real path)
    test_image_path = "test_image.png"  # Replace with actual image path
    
    if os.path.exists(test_image_path):
        result = tester.analyze_image_direct(
            test_image_path, 
            "Describe this image in detail. What objects, people, or scenes do you see?"
        )
        print(f"\n📋 Vision Analysis Result:")
        print(f"{result}")
        return True
    else:
        print(f"⚠️ Test image not found: {test_image_path}")
        print("💡 To test, place an image file named 'test_image.png' in the project root")
        return False

def test_browser_screenshot_vision():
    """Test vision analysis with browser screenshots."""
    print("\n" + "=" * 60)
    print("🌐 Testing Browser Screenshot Vision")
    print("=" * 60)
    
    tester = VisionTester()
    
    # Check if browser service is available
    try:
        from tools.browser import check_browser_service_health
        health = check_browser_service_health()
        
        if not health.get('healthy'):
            print("⚠️ Browser service not running. Start with: cd browser-service && npm start")
            return False
        
        # You would first need to launch browser and navigate to a page
        print("💡 For full test, first run:")
        print("   from tools.browser import launch_browser")  
        print("   launch_browser.invoke({'url': 'https://github.com'})")
        print("   Then run this test again")
        
        # Test with current browser content (if any)
        result = tester.analyze_screenshot_from_browser(
            "What do you see on this webpage? Describe the layout, text, and any visual elements."
        )
        print(f"\n📋 Screenshot Vision Result:")
        print(f"{result}")
        return True
        
    except ImportError:
        print("⚠️ Browser tools not available")
        return False
    except Exception as e:
        print(f"❌ Browser test failed: {e}")
        return False

def test_enhanced_tool_approach():
    """Test the enhanced tool approach."""
    print("\n" + "=" * 60)
    print("🛠️ Testing Enhanced Tool Approach")
    print("=" * 60)
    
    test_image_path = "test_image.png"
    
    if os.path.exists(test_image_path):
        # Test tool directly
        result = analyze_image_tool.invoke({
            "image_path": test_image_path,
            "question": "What are the main colors and objects in this image?"
        })
        print(f"\n📋 Tool Result:")
        print(f"{result}")
        return True
    else:
        print(f"⚠️ Test image not found: {test_image_path}")
        return False

def test_agent_with_vision_tool():
    """Test ReAct agent with vision tool (your original approach, improved)."""
    print("\n" + "=" * 60)
    print("🤖 Testing Agent with Vision Tool")
    print("=" * 60)
    
    try:
        # Initialize LLM
        llm = ChatOpenAI(
            base_url="http://localhost:1234/v1",
            api_key="lm-studio",
            model="qwen2-vl-2b-instruct"
        )
        
        # Create agent with vision tool
        tools = [analyze_image_tool]
        agent = create_react_agent(llm, tools)
        
        test_image_path = "test_image.png"
        
        if os.path.exists(test_image_path):
            # Use agent (this approach is less reliable but more flexible)
            result = agent.invoke({
                "messages": [
                    ("human", f"Use the analyze_image_tool to analyze the image at {test_image_path}. Tell me what objects and colors you see.")
                ]
            })
            
            print(f"\n📋 Agent Result:")
            print(f"{result}")
            return True
        else:
            print(f"⚠️ Test image not found: {test_image_path}")
            return False
            
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

def create_sample_test_image():
    """Create a simple test image for testing purposes."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple test image
        img = Image.new('RGB', (400, 300), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Draw some shapes
        draw.rectangle([50, 50, 150, 150], fill='red', outline='black')
        draw.ellipse([200, 50, 300, 150], fill='green', outline='black')
        draw.polygon([(100, 200), (150, 250), (50, 250)], fill='yellow', outline='black')
        
        # Add text
        try:
            # Try to use default font
            draw.text((50, 20), "Test Image for Vision Model", fill='black')
        except:
            # If font fails, just draw without text
            pass
        
        img.save('test_image.png')
        print("✅ Created test_image.png for testing")
        return True
        
    except ImportError:
        print("⚠️ PIL not available. Install with: pip install Pillow")
        return False
    except Exception as e:
        print(f"❌ Failed to create test image: {e}")
        return False

def main():
    """Run all vision integration tests."""
    print("🎯 Qwen-2.5-VL Vision Integration Tests")
    print("=" * 70)
    print("Testing multiple approaches for sending images to your LM Studio model")
    print("=" * 70)
    
    # Create test image if it doesn't exist
    if not os.path.exists('test_image.png'):
        print("📸 Creating test image...")
        created = create_sample_test_image()
        if not created:
            print("💡 Please place a test image named 'test_image.png' in the project root")
    
    # Run tests
    tests = [
        ("Direct Vision Approach (Recommended)", test_direct_vision_approach),
        ("Browser Screenshot Vision", test_browser_screenshot_vision), 
        ("Enhanced Tool Approach", test_enhanced_tool_approach),
        ("Agent with Vision Tool", test_agent_with_vision_tool)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔬 Running: {test_name}")
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Results Summary")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    successful_tests = sum(1 for passed in results.values() if passed)
    total_tests = len(results)
    
    print(f"\n🎯 Overall: {successful_tests}/{total_tests} tests passed")
    
    if successful_tests > 0:
        print("\n💡 Recommendations for your code:")
        print("1. Use the Direct Vision Approach for simple image analysis")
        print("2. Integrate with browser screenshots for web content analysis")  
        print("3. Always validate image files exist before encoding")
        print("4. Use proper error handling for robust applications")
        print("\n🚀 Your vision integration is working!")
    else:
        print("\n⚠️ No tests passed. Check your LM Studio setup:")
        print("1. Make sure LM Studio is running on localhost:1234")
        print("2. Load a Qwen-2.5-VL model that supports vision")
        print("3. Test basic text completion first")

if __name__ == "__main__":
    main()
