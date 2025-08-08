"""Browser automation tools using Patchright for stealth browsing - Single Session Architecture."""

from langchain_core.tools import tool
from patchright.sync_api import sync_playwright
from typing import Optional, Dict, Any
import logging
import os
import uuid
import time
import psutil
from pathlib import Path

logger = logging.getLogger(__name__)

class SingleSessionBrowserManager:
    """Simplified browser manager for single session architecture."""
    
    _instance = None
    _playwright = None
    _browser = None
    _current_session = None
    _browser_pid = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SingleSessionBrowserManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.screenshot_dir = Path("screenshots")
            self.screenshot_dir.mkdir(exist_ok=True)
            logger.info("SingleSessionBrowserManager initialized")
    
    def _kill_existing_browser(self):
        """Kill any existing browser process."""
        if self._browser_pid and self._is_process_running(self._browser_pid):
            try:
                logger.info(f"Terminating existing browser process (PID: {self._browser_pid})")
                process = psutil.Process(self._browser_pid)
                
                # Kill all child processes first
                for child in process.children(recursive=True):
                    try:
                        child.terminate()
                    except psutil.NoSuchProcess:
                        pass
                        
                # Kill main process
                process.terminate()
                
                # Wait for termination, force kill if needed
                try:
                    process.wait(timeout=5)
                except psutil.TimeoutExpired:
                    logger.warning("Browser didn't terminate gracefully, force killing...")
                    process.kill()
                    
                logger.info(f"Browser process {self._browser_pid} terminated")
                
            except psutil.NoSuchProcess:
                logger.info(f"Browser process {self._browser_pid} already terminated")
            except Exception as e:
                logger.error(f"Error killing browser process {self._browser_pid}: {e}")
        
        # Reset state
        self._browser = None
        self._browser_pid = None
        self._current_session = None
    
    def _is_process_running(self, pid):
        """Check if a process is still running."""
        try:
            return psutil.pid_exists(pid) and psutil.Process(pid).is_running()
        except:
            return False
    
    def launch_browser(self, url: str = "about:blank") -> Dict[str, Any]:
        """Launch a new browser session, killing any existing one."""
        try:
            # Kill any existing browser first
            self._kill_existing_browser()
            
            # Start new playwright instance
            if self._playwright:
                try:
                    self._playwright.stop()
                except:
                    pass
            
            self._playwright = sync_playwright().start()
            
            # Launch new browser
            self._browser = self._playwright.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--no-sandbox"
                ]
            )
            
            # Get browser process ID
            self._browser_pid = self._browser._impl_obj._connection._transport._proc.pid
            
            # Create new page
            page = self._browser.new_page()
            
            # Set realistic viewport and headers
            page.set_viewport_size({"width": 1366, "height": 768})
            page.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})
            
            # Create session info
            session_id = str(uuid.uuid4())
            self._current_session = {
                "session_id": session_id,
                "page": page,
                "browser_pid": self._browser_pid,
                "created_at": time.time(),
                "url": "about:blank"
            }
            
            logger.info(f"New browser launched (PID: {self._browser_pid}, Session: {session_id})")
            
            # Navigate if URL provided
            if url and url != "about:blank":
                try:
                    response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    if response and response.ok:
                        self._current_session["url"] = page.url
                        logger.info(f"Navigated to {page.url}")
                    else:
                        logger.warning(f"Navigation to {url} failed")
                except Exception as nav_error:
                    logger.error(f"Navigation error: {nav_error}")
            
            return self._current_session
            
        except Exception as e:
            logger.error(f"Failed to launch browser: {e}")
            self._kill_existing_browser()  # Cleanup on failure
            raise
    
    def get_current_session(self) -> Optional[Dict[str, Any]]:
        """Get the current active session."""
        if self._current_session and self._is_browser_alive():
            return self._current_session
        return None
    
    def _is_browser_alive(self) -> bool:
        """Check if the current browser is still alive."""
        if not self._browser_pid:
            return False
        return self._is_process_running(self._browser_pid)
    
    def take_screenshot(self, filename: str = None) -> str:
        """Take screenshot of current session."""
        session = self.get_current_session()
        if not session:
            raise ValueError("No active browser session")
        
        if filename is None:
            filename = f"screenshot_{session['session_id']}_{int(time.time())}.png"
        
        screenshot_path = self.screenshot_dir / filename
        
        try:
            session["page"].screenshot(path=str(screenshot_path))
            logger.info(f"Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            raise
    
    def close_browser(self):
        """Close the current browser session completely."""
        try:
            session_id = self._current_session["session_id"] if self._current_session else "unknown"
            self._kill_existing_browser()
            
            # Stop playwright
            if self._playwright:
                try:
                    self._playwright.stop()
                    self._playwright = None
                except Exception as e:
                    logger.error(f"Error stopping playwright: {e}")
            
            logger.info(f"Browser session {session_id} terminated completely")
            
        except Exception as e:
            logger.error(f"Error during browser cleanup: {e}")
            # Force cleanup even if there were errors
            self._browser = None
            self._browser_pid = None
            self._current_session = None

# Global browser manager instance
browser_manager = SingleSessionBrowserManager()

@tool
def launch_browser(url: str = "about:blank") -> str:
    """Launch a stealth browser and optionally navigate to a URL.
    
    This tool launches a new browser session, automatically terminating any existing browser.
    Only one browser session can be active at a time.
    
    Args:
        url: URL to navigate to after launch (default: blank page)
        
    Returns:
        Success message with session details
    """
    try:
        logger.info(f"Launching browser with URL: {url}")
        
        # Launch new browser (kills existing one automatically)
        session = browser_manager.launch_browser(url)
        
        # Take screenshot for verification
        screenshot_path = browser_manager.take_screenshot()
        
        return f"""🚀 Browser launched successfully!

📋 Session Details:
• Session ID: {session['session_id']}
• Process ID: {session['browser_pid']}
• Current URL: {session['url']}
• Screenshot: {screenshot_path}
• Status: Ready for interaction

The browser is now active and ready to use."""
        
    except Exception as e:
        error_msg = f"Failed to launch browser: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"

@tool
def close_browser() -> str:
    """Close the current browser session completely.
    
    This terminates the browser process and all associated resources.
    
    Returns:
        Confirmation message
    """
    try:
        session = browser_manager.get_current_session()
        if not session:
            return "📊 No active browser session to close"
        
        session_id = session['session_id']
        browser_pid = session['browser_pid']
        
        browser_manager.close_browser()
        
        return f"🔒 Browser session closed successfully!\n• Session ID: {session_id}\n• Process PID {browser_pid} terminated"
        
    except Exception as e:
        error_msg = f"Failed to close browser: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"

@tool
def get_browser_status() -> str:
    """Get status of the current browser session.
    
    Returns:
        Status report of active session
    """
    try:
        session = browser_manager.get_current_session()
        
        if not session:
            return "📊 No active browser session"
        
        created_at = time.strftime("%H:%M:%S", time.localtime(session["created_at"]))
        uptime = int(time.time() - session["created_at"])
        
        return f"""📊 Active Browser Session:
• Session ID: {session['session_id']}
• Process ID: {session['browser_pid']}
• Current URL: {session['url']}
• Created at: {created_at}
• Uptime: {uptime} seconds
• Status: Running"""
        
    except Exception as e:
        error_msg = f"Failed to get browser status: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"

# Cleanup function for graceful shutdown
def cleanup_browser():
    """Cleanup function to close browser resources."""
    try:
        browser_manager.close_browser()
        logger.info("Browser cleanup completed")
    except Exception as e:
        logger.error(f"Error during browser cleanup: {e}")
