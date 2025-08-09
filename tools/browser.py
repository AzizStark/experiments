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

logger = logging.getLogger(__name__)

# Browser service configuration
BROWSER_SERVICE_URL = "http://localhost:3000"
BROWSER_SERVICE_TIMEOUT = 30  # seconds

# Global session tracking
current_session_id: Optional[str] = None

class BrowserServiceError(Exception):
    """Exception raised when browser service operations fail."""
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
def take_marked_screenshot(options: Dict[str, Any] = None) -> Dict[str, Any]:
    """Take a screenshot with interactive elements highlighted.
    
    This advanced feature highlights clickable elements on the page,
    making it easier for AI models to identify interactive components.
    
    Args:
        options: Optional configuration for element marking
        
    Returns:
        Dictionary with marked screenshot and element data
    """
    global current_session_id
    
    try:
        if not current_session_id:
            return {
                "type": "error",
                "message": "❌ No active browser session. Please launch a browser first.",
                "image": None,
                "elements": []
            }
        
        logger.info(f"Taking marked screenshot: {current_session_id}")
        
        # Make request to capture marked screenshot
        response_data = _make_request("/browser/screenshot-marked", {
            "sessionId": current_session_id,
            "options": options or {}
        })
        
        logger.info("Marked screenshot captured successfully")
        
        return {
            "type": "marked_screenshot",
            "message": "📸 Marked screenshot captured with interactive elements highlighted.",
            "image": response_data.get("image"),
            "elements": response_data.get("elements", []),
            "session_id": response_data.get("sessionId"),
            "timestamp": response_data.get("timestamp")
        }
        
    except BrowserServiceError as e:
        error_msg = f"Failed to capture marked screenshot: {str(e)}"
        logger.error(error_msg)
        return {
            "type": "error", 
            "message": f"❌ {error_msg}",
            "image": None,
            "elements": []
        }
    except Exception as e:
        error_msg = f"Unexpected error capturing marked screenshot: {str(e)}"
        logger.error(error_msg)
        return {
            "type": "error", 
            "message": f"❌ {error_msg}",
            "image": None,
            "elements": []
        }

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
