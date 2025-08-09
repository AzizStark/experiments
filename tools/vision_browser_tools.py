"""
Vision-aware browser tools that combine navigation with automatic screenshot analysis.
These tools integrate browser automation with vision AI for autonomous web browsing.
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

class VisionBrowserError(Exception):
    """Exception raised when vision browser operations fail."""
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
            raise VisionBrowserError(f"Service error ({response.status_code}): {error_data.get('error', 'Unknown error')}")
            
    except requests.exceptions.ConnectionError:
        raise VisionBrowserError("Cannot connect to browser service. Is the service running on port 3000?")
    except requests.exceptions.Timeout:
        raise VisionBrowserError("Browser service request timed out")
    except requests.exceptions.RequestException as e:
        raise VisionBrowserError(f"Request failed: {str(e)}")

def _analyze_screenshot_with_vision(base64_image: str, question: str, current_url: str = "") -> str:
    """Send screenshot to vision model for analysis."""
    try:
        # Initialize vision model
        llm = ChatOpenAI(
            base_url="http://localhost:1234/v1",
            api_key="lm-studio",
            model="qwen2-vl-2b-instruct"  # Adjust to your model name
        )
        
        # Create context-aware question
        context_question = f"""You are analyzing a screenshot from the website: {current_url}

{question}

Please provide a detailed analysis of what you see on this webpage, including:
- Main visual elements and layout
- Text content and headings
- Interactive elements (buttons, links, forms)
- Images or graphics present
- Overall purpose and functionality of the page"""
        
        # Create multimodal message
        message = HumanMessage(
            content=[
                {"type": "text", "text": context_question},
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

@tool
def launch_browser_with_vision(url: str = "about:blank") -> str:
    """Launch browser and navigate to URL with automatic vision analysis.
    
    This tool launches a browser session and automatically analyzes the initial page.
    Perfect for starting autonomous browsing tasks.
    
    Args:
        url: URL to navigate to after launch
        
    Returns:
        Launch confirmation with initial page analysis
    """
    global current_session_id
    
    try:
        logger.info(f"Launching browser with vision analysis for: {url}")
        
        # Launch browser and navigate
        response_data = _make_request("/browser/launch", {"url": url})
        current_session_id = response_data.get("sessionId")
        
        # Wait for page to load
        time.sleep(3)
        
        # Automatically take screenshot and analyze
        screenshot_data = _make_request("/browser/screenshot", {"sessionId": current_session_id})
        base64_image = screenshot_data.get("screenshot_base64")
        
        if base64_image:
            # Analyze the page content
            analysis = _analyze_screenshot_with_vision(
                base64_image, 
                "What do you see on this webpage?",
                response_data.get('currentUrl', url)
            )
            
            return f"""🚀 Browser launched with vision analysis!

📋 Session Details:
• Session ID: {current_session_id}
• Current URL: {response_data.get('currentUrl')}
• Status: Ready for autonomous browsing

🔍 Initial Page Analysis:
{analysis}

The browser is now active and I can see the current page content."""
        else:
            return f"""🚀 Browser launched successfully!
• Session ID: {current_session_id}
• Current URL: {response_data.get('currentUrl')}
⚠️ Vision analysis failed - no screenshot data received"""
        
    except VisionBrowserError as e:
        error_msg = f"Failed to launch browser with vision: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error launching browser: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"

@tool
def navigate_and_analyze(url: str) -> str:
    """Navigate to a URL and automatically analyze what's visible with vision AI.
    
    This is the key tool for autonomous browsing - it navigates to a page and 
    immediately provides a detailed analysis of what's visible using vision AI.
    
    Args:
        url: URL to navigate to and analyze
        
    Returns:
        Navigation result with detailed vision analysis of the page
    """
    global current_session_id
    
    try:
        if not current_session_id:
            return "❌ No active browser session. Please launch a browser first."
        
        logger.info(f"Navigating to {url} with vision analysis")
        
        # Navigate to URL
        nav_response = _make_request("/browser/navigate", {
            "sessionId": current_session_id,
            "url": url
        })
        
        # Wait for page to load
        time.sleep(3)
        
        # Take screenshot for analysis
        screenshot_data = _make_request("/browser/screenshot", {"sessionId": current_session_id})
        base64_image = screenshot_data.get("screenshot_base64")
        current_url = nav_response.get('currentUrl', url)
        
        if base64_image:
            # Analyze the page content with vision
            analysis = _analyze_screenshot_with_vision(
                base64_image,
                "Analyze this webpage in detail. What do you see?",
                current_url
            )
            
            return f"""✅ Navigation and analysis complete!

🌐 Page Details:
• Target URL: {url}
• Final URL: {current_url}
• Analysis timestamp: {screenshot_data.get('timestamp')}

🔍 Vision Analysis:
{analysis}

Ready for next navigation or action."""
        else:
            return f"""✅ Navigation successful but vision analysis failed.
• Final URL: {current_url}
⚠️ No screenshot data received for analysis"""
        
    except VisionBrowserError as e:
        error_msg = f"Navigation/analysis to {url} failed: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected navigation error: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"

@tool
def analyze_current_page(question: str = "What do you see on this page?") -> str:
    """Analyze the current page with a specific question using vision AI.
    
    This tool takes a screenshot of the current page and analyzes it with vision AI,
    perfect for getting specific information about what's currently visible.
    
    Args:
        question: Specific question to ask about the current page
        
    Returns:
        Detailed vision analysis answering the specific question
    """
    global current_session_id
    
    try:
        if not current_session_id:
            return "❌ No active browser session. Please launch a browser first."
        
        logger.info(f"Analyzing current page with question: {question}")
        
        # Get current page status
        status_data = _make_request("/browser/status", {"sessionId": current_session_id})
        current_url = status_data.get('currentUrl', 'unknown')
        
        # Take screenshot
        screenshot_data = _make_request("/browser/screenshot", {"sessionId": current_session_id})
        base64_image = screenshot_data.get("screenshot_base64")
        
        if base64_image:
            # Analyze with specific question
            analysis = _analyze_screenshot_with_vision(base64_image, question, current_url)
            
            return f"""🔍 Current Page Analysis:

🌐 Page: {current_url}
❓ Question: {question}

📋 Analysis Result:
{analysis}"""
        else:
            return f"❌ Failed to capture screenshot for analysis of {current_url}"
        
    except VisionBrowserError as e:
        error_msg = f"Current page analysis failed: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected analysis error: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"

@tool
def compare_pages(urls: list, comparison_focus: str = "overall differences") -> str:
    """Navigate to multiple URLs and compare them using vision analysis.
    
    This tool is perfect for comparative analysis tasks, automatically visiting
    each URL and providing a structured comparison.
    
    Args:
        urls: List of URLs to visit and compare
        comparison_focus: What aspect to focus on when comparing
        
    Returns:
        Detailed comparison analysis of all visited pages
    """
    global current_session_id
    
    try:
        if not current_session_id:
            return "❌ No active browser session. Please launch a browser first."
        
        if len(urls) < 2:
            return "❌ Need at least 2 URLs to compare"
        
        logger.info(f"Comparing {len(urls)} pages with focus on: {comparison_focus}")
        
        analyses = []
        
        for i, url in enumerate(urls, 1):
            try:
                # Navigate to URL
                nav_response = _make_request("/browser/navigate", {
                    "sessionId": current_session_id,
                    "url": url
                })
                
                # Wait for page load
                time.sleep(3)
                
                # Take screenshot and analyze
                screenshot_data = _make_request("/browser/screenshot", {"sessionId": current_session_id})
                base64_image = screenshot_data.get("screenshot_base64")
                current_url = nav_response.get('currentUrl', url)
                
                if base64_image:
                    analysis = _analyze_screenshot_with_vision(
                        base64_image,
                        f"Analyze this webpage focusing on {comparison_focus}. Note key features for comparison.",
                        current_url
                    )
                    
                    analyses.append({
                        'url': current_url,
                        'analysis': analysis,
                        'index': i
                    })
                else:
                    analyses.append({
                        'url': current_url,
                        'analysis': f"❌ Failed to capture screenshot for {url}",
                        'index': i
                    })
                    
            except Exception as e:
                analyses.append({
                    'url': url,
                    'analysis': f"❌ Failed to analyze {url}: {str(e)}",
                    'index': i
                })
        
        # Create comparison summary
        comparison_result = f"""🔍 Multi-Page Comparison Analysis

📊 Comparison Focus: {comparison_focus}
🌐 Pages Analyzed: {len(analyses)}

"""
        
        for analysis in analyses:
            comparison_result += f"""
{'='*50}
🔗 Page {analysis['index']}: {analysis['url']}
{'='*50}

{analysis['analysis']}

"""
        
        comparison_result += f"""
{'='*50}
📋 COMPARISON SUMMARY
{'='*50}

Based on the analysis of all {len(analyses)} pages, here are the key differences and similarities:

[The vision model would provide detailed comparisons here based on the individual analyses]
"""
        
        return comparison_result
        
    except VisionBrowserError as e:
        error_msg = f"Page comparison failed: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected comparison error: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"

@tool 
def close_browser_session() -> str:
    """Close the current browser session and cleanup.
    
    Returns:
        Confirmation message
    """
    global current_session_id
    
    try:
        if not current_session_id:
            return "📊 No active browser session to close"
        
        logger.info(f"Closing browser session: {current_session_id}")
        
        # Close session
        response_data = _make_request("/browser/close", {"sessionId": current_session_id})
        
        session_id = current_session_id
        current_session_id = None  # Reset global session
        
        return f"🔒 Browser session closed successfully!\n• Session ID: {session_id}\n• Vision analysis complete"
        
    except VisionBrowserError as e:
        error_msg = f"Failed to close browser session: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error closing browser: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"

def check_vision_browser_health() -> Dict[str, Any]:
    """Check if both browser service and vision model are available."""
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
        # Simple test
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
