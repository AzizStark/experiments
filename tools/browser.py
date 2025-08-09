"""
Professional browser automation tools using Node.js service with @presidio-dev/playwright-core.
Provides reliable, enterprise-grade browser control.
"""

from langchain_core.tools import tool
from typing import Dict, Any, Optional
import requests
import logging
import time
import json
import base64
from PIL import Image
import io

logger = logging.getLogger(__name__)

# Browser service configuration
BROWSER_SERVICE_URL = "http://localhost:3000"
BROWSER_SERVICE_TIMEOUT = 30  # seconds

# Moondream service configuration
MOONDREAM_URL = "http://localhost:2020/v1"
MOONDREAM_TIMEOUT = 30  # seconds

# Global session tracking
current_session_id: Optional[str] = None

class BrowserServiceError(Exception):
    """Exception raised when browser service operations fail."""
    pass

class MoondreamError(Exception):
    """Exception raised when Moondream operations fail."""
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
            raise BrowserServiceError(f"Service error ({response.status_code}): {error_data.get('error', 'Unknown error')}")
            
    except requests.exceptions.ConnectionError:
        raise BrowserServiceError("Cannot connect to browser service. Is the service running on port 3000?")
    except requests.exceptions.Timeout:
        raise BrowserServiceError("Browser service request timed out")
    except requests.exceptions.RequestException as e:
        raise BrowserServiceError(f"Request failed: {str(e)}")

def _encode_image_to_base64(image_data: bytes) -> str:
    """Encode image bytes to base64 string for Moondream API."""
    encoded = base64.b64encode(image_data).decode('utf-8')
    return f"data:image/png;base64,{encoded}"

def _find_element_coordinates(element_description: str) -> Optional[Dict[str, int]]:
    """Use Moondream to find element coordinates from description."""
    global current_session_id
    
    if not current_session_id:
        raise MoondreamError("No active browser session for screenshot")
    
    try:
        # Take screenshot first
        logger.info(f"Taking screenshot for element detection: {element_description}")
        screenshot_response = _make_request("/browser/screenshot", {"sessionId": current_session_id})
        
        # Get screenshot data
        screenshot_base64 = screenshot_response.get("screenshot_base64")
        if not screenshot_base64:
            raise MoondreamError("Failed to capture screenshot")
        
        # Decode base64 to get image dimensions
        # Remove data URL prefix if present
        if screenshot_base64.startswith('data:'):
            screenshot_base64 = screenshot_base64.split(',')[1]
        
        image_bytes = base64.b64decode(screenshot_base64)
        image = Image.open(io.BytesIO(image_bytes))
        width, height = image.size
        
        logger.info(f"Screenshot dimensions: {width}x{height}")
        
        # Prepare Moondream request
        moondream_data = {
            "image_url": _encode_image_to_base64(image_bytes),
            "object": element_description
        }
        
        # Send to Moondream pointing endpoint
        logger.info(f"Sending to Moondream: {element_description}")
        response = requests.post(
            f"{MOONDREAM_URL}/point",
            json=moondream_data,
            timeout=MOONDREAM_TIMEOUT
        )
        
        if response.status_code != 200:
            raise MoondreamError(f"Moondream API error: {response.status_code}")
        
        result = response.json()
        
        # Process coordinates
        if "points" in result and result["points"]:
            point = result["points"][0]  # Take first point
            
            # Convert normalized coordinates to pixels
            norm_x = point.get("x", 0)
            norm_y = point.get("y", 0)
            pixel_x = int(norm_x * width)
            pixel_y = int(norm_y * height)
            
            logger.info(f"Found element at: ({pixel_x}, {pixel_y})")
            
            return {
                "x": pixel_x,
                "y": pixel_y,
                "normalized_x": norm_x,
                "normalized_y": norm_y,
                "width": width,
                "height": height
            }
        else:
            logger.warning(f"Moondream could not find: {element_description}")
            return None
            
    except requests.exceptions.ConnectionError:
        raise MoondreamError("Cannot connect to Moondream server at localhost:2020")
    except Exception as e:
        raise MoondreamError(f"Element detection failed: {str(e)}")

@tool
def launch_browser(url: str = "about:blank") -> str:
    """Launch browser and navigate to URL with enterprise-grade reliability.
    
    This tool launches a browser session using our professional browser service
    powered by @presidio-dev/playwright-core, specifically designed for LLM use cases.
    
    Args:
        url: URL to navigate to after launch (default: blank page)
        
    Returns:
        Success message with session details
    """
    global current_session_id
    
    try:
        logger.info(f"Launching browser with URL: {url}")
        
        # Make request to browser service
        response_data = _make_request("/browser/launch", {"url": url})
        
        # Store session ID for future operations
        current_session_id = response_data.get("sessionId")
        
        return f"""🚀 Browser launched successfully!

📋 Session Details:
• Session ID: {current_session_id}
• Current URL: {response_data.get('currentUrl')}
• Architecture: Enterprise-grade browser service
• Status: Ready for interaction and vision analysis

The browser is now active and ready to use."""
        
    except BrowserServiceError as e:
        error_msg = f"Failed to launch browser: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error launching browser: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"

@tool
def close_browser() -> str:
    """Close the current browser session.
    
    Returns:
        Confirmation message
    """
    global current_session_id
    
    try:
        if not current_session_id:
            return "📊 No active browser session to close"
        
        logger.info(f"Closing browser session: {current_session_id}")
        
        # Make request to close session
        response_data = _make_request("/browser/close", {"sessionId": current_session_id})
        
        session_id = current_session_id
        current_session_id = None  # Reset global session
        
        return f"🔒 Browser session closed successfully!\n• Session ID: {session_id}"
        
    except BrowserServiceError as e:
        error_msg = f"Failed to close browser: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error closing browser: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"

@tool
def get_browser_status() -> str:
    """Get status of the current browser session.
    
    Returns:
        Status report of active session
    """
    global current_session_id
    
    try:
        if not current_session_id:
            return "📊 No active browser session"
        
        logger.info(f"Getting browser status: {current_session_id}")
        
        # Make request to get status
        response_data = _make_request("/browser/status", {"sessionId": current_session_id})
        
        return f"""📊 Active Browser Session:
• Session ID: {response_data.get('sessionId')}
• Current URL: {response_data.get('currentUrl')}
• Tab Count: {response_data.get('tabCount', 1)}
• Status: {response_data.get('status')}
• Architecture: {response_data.get('architecture')}
• Reliability: Enterprise-grade ✅"""
        
    except BrowserServiceError as e:
        error_msg = f"Failed to get browser status: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error getting status: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"

@tool 
def analyze_screen() -> Dict[str, Any]:
    """Take a screenshot for vision analysis.
    
    This tool captures the current browser screen and returns the image data
    for processing by vision-capable AI models. Uses enterprise-grade browser
    automation for 100% reliable screenshot capture.
    
    Returns:
        Dictionary containing screenshot data and metadata for LLM processing
    """
    global current_session_id
    
    try:
        if not current_session_id:
            return {
                "type": "error",
                "message": "❌ No active browser session. Please launch a browser first.",
                "screenshot_base64": None
            }
        
        logger.info(f"Taking screenshot: {current_session_id}")
        
        # Make request to capture screenshot
        response_data = _make_request("/browser/screenshot", {"sessionId": current_session_id})
        
        logger.info("Screenshot captured successfully")
        
        return {
            "type": "screenshot",
            "message": "📸 Screenshot captured successfully for vision analysis.",
            "screenshot_base64": response_data.get("screenshot_base64"),
            "session_id": response_data.get("sessionId"),
            "current_url": response_data.get("currentUrl"),
            "timestamp": response_data.get("timestamp"),
            "architecture": response_data.get("architecture", "enterprise-browser-service")
        }
        
    except BrowserServiceError as e:
        error_msg = f"Failed to capture screenshot: {str(e)}"
        logger.error(error_msg)
        return {
            "type": "error", 
            "message": f"❌ {error_msg}",
            "screenshot_base64": None
        }
    except Exception as e:
        error_msg = f"Unexpected error capturing screenshot: {str(e)}"
        logger.error(error_msg)
        return {
            "type": "error", 
            "message": f"❌ {error_msg}",
            "screenshot_base64": None
        }

@tool
def navigate_to_url(url: str) -> str:
    """Navigate to a specific URL in the current session.
    
    Args:
        url: URL to navigate to
        
    Returns:
        Navigation result message
    """
    global current_session_id
    
    try:
        if not current_session_id:
            return "❌ No active browser session. Please launch a browser first."
        
        logger.info(f"Navigating to: {url}")
        
        # Make request to navigate
        response_data = _make_request("/browser/navigate", {
            "sessionId": current_session_id,
            "url": url
        })
        
        return f"""✅ Navigation successful!
• Target URL: {response_data.get('targetUrl')}
• Final URL: {response_data.get('currentUrl')}
• Session: {response_data.get('sessionId')}"""
        
    except BrowserServiceError as e:
        error_msg = f"Navigation to {url} failed: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected navigation error: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"

@tool
def click(x: int, y: int) -> str:
    """Click at specific coordinates on the page.
    
    Args:
        x: X coordinate to click
        y: Y coordinate to click
        
    Returns:
        Click result message
    """
    global current_session_id
    
    try:
        if not current_session_id:
            return "❌ No active browser session. Please launch a browser first."
        
        logger.info(f"Clicking at coordinates: ({x}, {y})")
        
        # Make request to click
        response_data = _make_request("/browser/click", {
            "sessionId": current_session_id,
            "x": x,
            "y": y
        })
        
        return f"""✅ Click performed successfully!
• Coordinates: ({x}, {y})
• Session: {response_data.get('sessionId')}"""
        
    except BrowserServiceError as e:
        error_msg = f"Click at ({x}, {y}) failed: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected click error: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"

@tool
def find_and_click(element_description: str) -> str:
    """Find an element on screen using natural language and click it.
    
    Uses Moondream vision model to locate elements by description and clicks them.
    
    Args:
        element_description: Natural language description of the element
                           Examples: "cart icon at top right"
                                    "login button at the bottom of form"
                                    "red search button"
                                    "username input field"
    
    Returns:
        Result message with click status
    """
    global current_session_id
    
    try:
        if not current_session_id:
            return "❌ No active browser session. Please launch a browser first."
        
        logger.info(f"Finding and clicking element: {element_description}")
        
        # Find element coordinates using Moondream
        coords = _find_element_coordinates(element_description)
        
        if not coords:
            return f"""❌ Could not find element: "{element_description}"

💡 Tips for better element descriptions:
• Be specific: "blue submit button" instead of just "button"
• Include location: "search box at top of page"
• Mention text: "button with text 'Login'"
• Use visual features: "red circular icon"

Try rephrasing your description or take a screenshot to see what's on the page."""
        
        # Click at the found coordinates
        logger.info(f"Clicking at found coordinates: ({coords['x']}, {coords['y']})")
        
        click_response = _make_request("/browser/click", {
            "sessionId": current_session_id,
            "x": coords['x'],
            "y": coords['y']
        })
        
        return f"""✅ Successfully found and clicked: "{element_description}"

📍 Element Details:
• Found at: ({coords['x']}, {coords['y']})
• Normalized position: ({coords['normalized_x']:.3f}, {coords['normalized_y']:.3f})
• Screen size: {coords['width']}x{coords['height']}
• Session: {current_session_id}

The element has been clicked successfully!"""
        
    except MoondreamError as e:
        error_msg = f"Vision detection failed: {str(e)}"
        logger.error(error_msg)
        return f"""❌ {error_msg}

💡 Make sure:
• Moondream server is running on localhost:2020
• The browser has a page loaded
• The element description is clear and specific"""
        
    except BrowserServiceError as e:
        error_msg = f"Browser operation failed: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"

@tool
def type_text(text: str) -> str:
    """Type text into the currently focused element.
    
    Args:
        text: Text to type
        
    Returns:
        Type result message
    """
    global current_session_id
    
    try:
        if not current_session_id:
            return "❌ No active browser session. Please launch a browser first."
        
        logger.info(f"Typing text: {text}")
        
        # Make request to type
        response_data = _make_request("/browser/type", {
            "sessionId": current_session_id,
            "text": text
        })
        
        return f"""✅ Text typed successfully!
• Text: "{text}"
• Session: {response_data.get('sessionId')}"""
        
    except BrowserServiceError as e:
        error_msg = f"Failed to type text: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected typing error: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"

def check_browser_service_health() -> Dict[str, Any]:
    """Check if the browser service is running and healthy."""
    try:
        response_data = _make_request("/health", method="GET")
        return {
            "healthy": True,
            "status": response_data.get("status"),
            "activeSessions": response_data.get("activeSessions", []),
            "timestamp": response_data.get("timestamp")
        }
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "message": "Browser service is not running. Please start it with: cd browser-service && npm start"
        }

def check_moondream_health() -> Dict[str, Any]:
    """Check if Moondream service is accessible."""
    try:
        response = requests.get(f"{MOONDREAM_URL}/health", timeout=5)
        return {
            "healthy": True,
            "status": f"Moondream server responsive (Status: {response.status_code})"
        }
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "message": "Moondream service is not running on localhost:2020"
        }

# Cleanup function
def cleanup_browser():
    """Cleanup function for browser service."""
    global current_session_id
    
    try:
        if current_session_id:
            logger.info("Cleaning up browser session")
            _make_request("/browser/close", {"sessionId": current_session_id})
            current_session_id = None
        
        # Close all sessions
        _make_request("/browser/close-all")
        logger.info("Browser cleanup completed")
        
    except Exception as e:
        logger.error(f"Error during browser cleanup: {e}")
