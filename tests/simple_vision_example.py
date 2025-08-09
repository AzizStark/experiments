"""
Simple corrected example for vision integration with Qwen-2.5-VL.
This fixes the issues in your original code and provides working examples.
"""

import sys
import os
import base64
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

# ========================================
# APPROACH 1: Direct LLM Call (RECOMMENDED)
# ========================================

def analyze_image_direct(image_path: str, question: str) -> str:
    """
    Direct approach - most reliable for vision tasks.
    This is the corrected version of what you want to do.
    """
    # Initialize model
    llm = ChatOpenAI(
        base_url="http://localhost:1234/v1",
        api_key="lm-studio",
        model="qwen2-vl-2b-instruct"  # Adjust to your model name
    )
    
    # Validate file exists
    if not os.path.exists(image_path):
        return f"❌ Image file not found: {image_path}"
    
    # Encode image to base64
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        return f"❌ Failed to read image: {str(e)}"
    
    # Detect image format
    extension = Path(image_path).suffix.lower()
    image_format = 'jpeg' if extension in ['.jpg', '.jpeg'] else 'png'
    
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
    
    # Send to model and get response
    try:
        response = llm.invoke([message])
        return response.content
    except Exception as e:
        return f"❌ Vision analysis failed: {str(e)}"

# ========================================
# APPROACH 2: Fixed Tool Version
# ========================================

@tool
def analyze_image_fixed(image_path: str, question: str) -> str:
    """
    Fixed version of your original tool.
    This addresses the issues in your code.
    """
    return analyze_image_direct(image_path, question)

# ========================================
# APPROACH 3: Agent with Tool (Your Original Approach - Fixed)
# ========================================

def analyze_with_agent(image_path: str, question: str) -> str:
    """
    Your original agent approach, but fixed.
    Less reliable than direct approach, but more flexible.
    """
    # Initialize model
    llm = ChatOpenAI(
        base_url="http://localhost:1234/v1",
        api_key="lm-studio",
        model="qwen2-vl-2b-instruct"
    )
    
    # Create agent with fixed tool
    tools = [analyze_image_fixed]
    agent = create_react_agent(llm, tools)
    
    # BETTER: Call tool directly instead of asking agent to parse file path
    try:
        result = analyze_image_fixed.invoke({
            "image_path": image_path,
            "question": question
        })
        return result
    except Exception as e:
        return f"❌ Agent analysis failed: {str(e)}"

# ========================================
# INTEGRATION WITH YOUR BROWSER SERVICE
# ========================================

def analyze_browser_screenshot(question: str) -> str:
    """
    Analyze current browser screenshot using vision model.
    This integrates with your existing browser automation.
    """
    try:
        # Import your browser tools
        from tools.browser import analyze_screen
        
        # Get screenshot from your browser service
        screenshot_result = analyze_screen.invoke({})
        
        if screenshot_result.get('type') != 'screenshot':
            return f"❌ Failed to get screenshot: {screenshot_result.get('message')}"
        
        base64_image = screenshot_result.get('screenshot_base64')
        if not base64_image:
            return "❌ No screenshot data received"
        
        # Initialize LLM
        llm = ChatOpenAI(
            base_url="http://localhost:1234/v1",
            api_key="lm-studio",
            model="qwen2-vl-2b-instruct"
        )
        
        # Create multimodal message with screenshot
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
        response = llm.invoke([message])
        return response.content
        
    except Exception as e:
        return f"❌ Screenshot vision analysis failed: {str(e)}"

# ========================================
# USAGE EXAMPLES
# ========================================

def main():
    """Demonstrate all approaches."""
    print("🎯 Simple Vision Integration Examples")
    print("=" * 50)
    
    # Test image path (replace with your actual image)
    test_image = "test_image.png"
    question = "What objects and colors do you see in this image?"
    
    if not os.path.exists(test_image):
        print(f"⚠️ Please place an image named '{test_image}' in the project root to test")
        return
    
    print("\n1️⃣ Direct Approach (Recommended):")
    print("-" * 40)
    result1 = analyze_image_direct(test_image, question)
    print(f"Result: {result1}")
    
    print("\n2️⃣ Fixed Tool Approach:")
    print("-" * 40)
    result2 = analyze_with_agent(test_image, question)
    print(f"Result: {result2}")
    
    print("\n3️⃣ Browser Screenshot Analysis:")
    print("-" * 40)
    print("💡 First launch browser with your tools:")
    print("   from tools.browser import launch_browser")
    print("   launch_browser.invoke({'url': 'https://github.com'})")
    print("   Then run: analyze_browser_screenshot('What do you see?')")
    
    # Uncomment to test browser integration:
    # result3 = analyze_browser_screenshot("What do you see on this webpage?")
    # print(f"Result: {result3}")

if __name__ == "__main__":
    main()

# ========================================
# WHAT WAS WRONG WITH YOUR ORIGINAL CODE:
# ========================================

"""
Your Original Code Issues:
1. Agent had to parse file path from natural language - unreliable
2. No error handling for missing files or encoding failures  
3. Agent invocation was complex and prone to failure
4. No image format detection

Fixed Version Benefits:
1. Direct tool invocation - much more reliable
2. Proper error handling throughout
3. Image format detection
4. Integration with your browser service
5. Multiple approaches for different use cases

Recommendation: Use the direct approach (analyze_image_direct) for most cases.
"""
