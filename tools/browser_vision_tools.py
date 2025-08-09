"""
Simple CLI-style browser automation tools with automatic vision analysis.
Each tool performs an action and automatically sends the result to the vision LLM.
"""

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from typing import Dict, Any, Optional
import requests
import logging
import time
import base64

logger = logging.getLogger(__name__)

# Browser service configuration
BROWSER_SERVICE_URL = "http://localhost:3000"
BROWSER_SERVICE_TIMEOUT = 30

# Global session tracking
current_session_id: Optional[str] = None

class BrowserError(Exception):
    """Exception raised when browser operations fail."""
    pass

def _make_request(endpoint: str, data: Dict[str, Any] = None, method: str = "POST") -> Dict[str, Any]:
    """Make HTTP request to browser service with error handling."""
    try:
        url = f"{BROWSER_SERVICE_URL}{endpoint}"
        
        if method.upper() == "GET":
            response = requests.get(url, timeout=BROWSER_SERVICE_TIMEOUT)
        else:
            response = requests.post(url, json=data or {}, timeout=BROWSER_SERVICE_TIMEOUT)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"error": response.text}
            raise BrowserError(f"Service error ({response.status_code}): {error_data.get('error', 'Unknown error')}")
            
    except requests.exceptions.ConnectionError:
        raise BrowserError("Cannot connect to browser service. Is the service running on port 3000?")
    except requests.exceptions.Timeout:
        raise BrowserError("Browser service request timed out")
    except requests.exceptions.RequestException as e:
        raise BrowserError(f"Request failed: {str(e)}")

def _analyze_with_vision(base64_image: str, action_context: str, current_url: str = "") -> str:
    """Send screenshot to vision model with action context."""
    try:
        # Initialize vision model
        llm = ChatOpenAI(
            base_url="http://localhost:1234/v1",
            api_key="lm-studio",
            model="qwen2-vl-2b-instruct"
        )
        
        # Create context-aware question
        vision_prompt = f"""You are analyzing a screenshot after this browser action: {action_context}

Current webpage: {current_url}

Describe what you see on the screen now, including:
- What changed as a result of the action
- Current page content and layout
- Interactive elements visible (buttons, links, forms, etc.)
- Any error messages or loading states
- Overall state of the webpage

Be specific about what you observe so I can plan the next action."""
        
        # Create multimodal message
        message = HumanMessage(
            content=[
                {"type": "text", "text": vision_prompt},
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
        return f"❌ Vision analysis failed: {str(e)}"

def _take_screenshot_and_analyze(action_context: str) -> str:
    """Take screenshot and analyze with vision after any browser action."""
    global current_session_id
    
    try:
        if not current_session_id:
            return f"Action completed but no browser session active for vision analysis."
        
        # Take screenshot
        screenshot_data = _make_request("/browser/screenshot", {"sessionId": current_session_id})
        base64_image = screenshot_data.get("screenshot_base64")
        current_url = screenshot_data.get("currentUrl", "unknown")
        
        if base64_image:
            # Analyze with vision
            vision_analysis = _analyze_with_vision(base64_image, action_context, current_url)
            return f"""Action completed successfully.

🔍 What I see on screen:
{vision_analysis}"""
        else:
            return f"Action completed but screenshot capture failed."
            
    except Exception as e:
        return f"Action completed but vision analysis failed: {str(e)}"

@tool
def launch(url: str = "about:blank") -> str:
    """Launch browser and navigate to URL. Always use this first."""
    global current_session_id
    
    try:
        logger.info(f"Launching browser: {url}")
        
        # Launch browser and navigate
        response_data = _make_request("/browser/launch", {"url": url})
        current_session_id = response_data.get("sessionId")
        
        # Wait for page load
        time.sleep(2)
        
        # Analyze what we see
        analysis = _take_screenshot_and_analyze(f"Launched browser and navigated to {url}")
        
        return f"""🚀 Browser launched successfully!
Session ID: {current_session_id}
Current URL: {response_data.get('currentUrl')}

{analysis}"""
        
    except BrowserError as e:
        return f"❌ Failed to launch browser: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

@tool
def navigate(url: str) -> str:
    """Navigate to a new URL."""
    global current_session_id
    
    try:
        if not current_session_id:
            return "❌ No browser session. Use 'launch' first."
        
        logger.info(f"Navigating to: {url}")
        
        # Navigate to URL
        nav_response = _make_request("/browser/navigate", {
            "sessionId": current_session_id,
            "url": url
        })
        
        # Wait for page load
        time.sleep(2)
        
        # Analyze what we see
        analysis = _take_screenshot_and_analyze(f"Navigated to {url}")
        
        return f"""✅ Navigation successful!
Final URL: {nav_response.get('currentUrl')}

{analysis}"""
        
    except BrowserError as e:
        return f"❌ Navigation failed: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

@tool
def click(x: int, y: int) -> str:
    """Click at coordinates x,y on the page."""
    global current_session_id
    
    try:
        if not current_session_id:
            return "❌ No browser session. Use 'launch' first."
        
        logger.info(f"Clicking at coordinates: ({x}, {y})")
        
        # Perform click (using browser service API)
        click_response = _make_request("/browser/click", {
            "sessionId": current_session_id,
            "x": x,
            "y": y
        })
        
        # Wait for any page changes
        time.sleep(1)
        
        # Analyze what happened
        analysis = _take_screenshot_and_analyze(f"Clicked at coordinates ({x}, {y})")
        
        return f"""✅ Click performed at ({x}, {y})

{analysis}"""
        
    except BrowserError as e:
        return f"❌ Click failed: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

@tool
def type_text(text: str) -> str:
    """Type text into the currently focused element."""
    global current_session_id
    
    try:
        if not current_session_id:
            return "❌ No browser session. Use 'launch' first."
        
        logger.info(f"Typing text: {text}")
        
        # Type text (using browser service API)
        type_response = _make_request("/browser/type", {
            "sessionId": current_session_id,
            "text": text
        })
        
        # Wait for any changes
        time.sleep(0.5)
        
        # Analyze what happened
        analysis = _take_screenshot_and_analyze(f"Typed text: '{text}'")
        
        return f"""✅ Text typed: "{text}"

{analysis}"""
        
    except BrowserError as e:
        return f"❌ Typing failed: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

@tool
def scroll(direction: str = "down", amount: int = 3) -> str:
    """Scroll the page. Direction: 'up' or 'down'. Amount: number of scroll steps."""
    global current_session_id
    
    try:
        if not current_session_id:
            return "❌ No browser session. Use 'launch' first."
        
        if direction not in ["up", "down"]:
            return "❌ Direction must be 'up' or 'down'"
        
        logger.info(f"Scrolling {direction} by {amount} steps")
        
        # Scroll (using browser service API)
        scroll_response = _make_request("/browser/scroll", {
            "sessionId": current_session_id,
            "direction": direction,
            "amount": amount
        })
        
        # Wait for scroll to complete
        time.sleep(0.5)
        
        # Analyze what we see now
        analysis = _take_screenshot_and_analyze(f"Scrolled {direction} by {amount} steps")
        
        return f"""✅ Scrolled {direction} by {amount} steps

{analysis}"""
        
    except BrowserError as e:
        return f"❌ Scroll failed: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

@tool
def look() -> str:
    """Take a screenshot and analyze what's currently visible on screen."""
    global current_session_id
    
    try:
        if not current_session_id:
            return "❌ No browser session. Use 'launch' first."
        
        logger.info("Taking screenshot for analysis")
        
        # Just analyze current screen
        analysis = _take_screenshot_and_analyze("Looking at current screen")
        
        return analysis
        
    except Exception as e:
        return f"❌ Screenshot analysis failed: {str(e)}"

@tool
def close() -> str:
    """Close the browser session."""
    global current_session_id
    
    try:
        if not current_session_id:
            return "📊 No active browser session to close"
        
        logger.info(f"Closing browser session: {current_session_id}")
        
        # Close session
        response_data = _make_request("/browser/close", {"sessionId": current_session_id})
        
        session_id = current_session_id
        current_session_id = None  # Reset global session
        
        return f"🔒 Browser session closed successfully!\nSession ID: {session_id}"
        
    except BrowserError as e:
        return f"❌ Failed to close browser: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

@tool
def status() -> str:
    """Get current browser session status."""
    global current_session_id
    
    try:
        if not current_session_id:
            return "📊 No active browser session"
        
        # Get status
        response_data = _make_request("/browser/status", {"sessionId": current_session_id})
        
        return f"""📊 Browser Session Status:
• Session ID: {response_data.get('sessionId')}
• Current URL: {response_data.get('currentUrl')}
• Status: {response_data.get('status')}
• Active: ✅"""
        
    except BrowserError as e:
        return f"❌ Status check failed: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

def check_health() -> Dict[str, Any]:
    """Check if browser service and vision model are available."""
    try:
        # Check browser service
        browser_response = _make_request("/health", method="GET")
        browser_healthy = True
        browser_status = browser_response.get("status")
    except Exception as e:
        browser_healthy = False
        browser_status = f"Browser service error: {str(e)}"
    
    # Check vision model
    try:
        llm = ChatOpenAI(
            base_url="http://localhost:1234/v1",
            api_key="lm-studio",
            model="qwen2-vl-2b-instruct"
        )
        test_response = llm.invoke([HumanMessage(content="Hello")])
        vision_healthy = True
        vision_status = "Vision model responsive"
    except Exception as e:
        vision_healthy = False
        vision_status = f"Vision model error: {str(e)}"
    
    return {
        "browser_service": {
            "healthy": browser_healthy,
            "status": browser_status
        },
        "vision_model": {
            "healthy": vision_healthy,
            "status": vision_status
        },
        "overall_healthy": browser_healthy and vision_healthy,
        "message": "All systems ready" if (browser_healthy and vision_healthy) else "Some services have issues"
    }
