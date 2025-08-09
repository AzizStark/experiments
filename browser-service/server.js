const express = require('express');
const cors = require('cors');
const { BrowserService, navigate, getCurrentUrl, click, type, wait } = require('@presidio-dev/playwright-core');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Store active sessions
const activeSessions = new Set();

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    activeSessions: Array.from(activeSessions)
  });
});

// Launch browser and navigate to URL
app.post('/browser/launch', async (req, res) => {
  try {
    const { url = 'about:blank' } = req.body;
    const sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    console.log(`🚀 Launching browser session ${sessionId} with URL: ${url}`);
    
    // Navigate to URL (this will create the browser session if needed)
    await navigate(sessionId, url);
    
    // Get current URL after navigation
    const currentUrl = await getCurrentUrl(sessionId);
    
    // Track active session
    activeSessions.add(sessionId);
    
    console.log(`✅ Browser session ${sessionId} launched successfully`);
    
    res.json({
      success: true,
      sessionId: sessionId,
      currentUrl: currentUrl,
      message: `Browser launched successfully with session ${sessionId}`
    });
    
  } catch (error) {
    console.error('❌ Failed to launch browser:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to launch browser'
    });
  }
});

// Take screenshot for vision analysis
app.post('/browser/screenshot', async (req, res) => {
  try {
    const { sessionId } = req.body;
    
    if (!sessionId) {
      return res.status(400).json({
        success: false,
        error: 'Session ID is required'
      });
    }
    
    if (!activeSessions.has(sessionId)) {
      return res.status(404).json({
        success: false,
        error: 'Session not found'
      });
    }
    
    console.log(`📸 Taking screenshot for session ${sessionId}`);
    
    // Get browser service instance
    const browser = BrowserService.getInstance();
    
    // Take screenshot with base64 encoding
    const screenshotBase64 = await browser.takeScreenshot(sessionId, 1000); // 1s min wait
    
    // Get current URL for metadata
    const currentUrl = await getCurrentUrl(sessionId);
    
    console.log(`✅ Screenshot captured for session ${sessionId}`);
    
    res.json({
      type: 'screenshot',
      success: true,
      screenshot_base64: screenshotBase64,
      sessionId: sessionId,
      currentUrl: currentUrl,
      timestamp: Date.now(),
      message: 'Screenshot captured successfully',
      architecture: 'node-playwright-core'
    });
    
  } catch (error) {
    console.error('❌ Failed to take screenshot:', error);
    res.status(500).json({
      type: 'error',
      success: false,
      error: error.message,
      message: 'Failed to capture screenshot'
    });
  }
});

// Navigate to a new URL in existing session
app.post('/browser/navigate', async (req, res) => {
  try {
    const { sessionId, url } = req.body;
    
    if (!sessionId || !url) {
      return res.status(400).json({
        success: false,
        error: 'Session ID and URL are required'
      });
    }
    
    if (!activeSessions.has(sessionId)) {
      return res.status(404).json({
        success: false,
        error: 'Session not found'
      });
    }
    
    console.log(`🧭 Navigating session ${sessionId} to ${url}`);
    
    // Navigate to new URL
    await navigate(sessionId, url);
    
    // Get final URL
    const currentUrl = await getCurrentUrl(sessionId);
    
    console.log(`✅ Navigation successful for session ${sessionId}`);
    
    res.json({
      success: true,
      sessionId: sessionId,
      targetUrl: url,
      currentUrl: currentUrl,
      message: 'Navigation successful'
    });
    
  } catch (error) {
    console.error('❌ Navigation failed:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Navigation failed'
    });
  }
});

// Get browser status
app.post('/browser/status', async (req, res) => {
  try {
    const { sessionId } = req.body;
    
    if (!sessionId) {
      return res.status(400).json({
        success: false,
        error: 'Session ID is required'
      });
    }
    
    if (!activeSessions.has(sessionId)) {
      return res.status(404).json({
        success: false,
        error: 'Session not found',
        activeSessions: Array.from(activeSessions)
      });
    }
    
    // Get current URL and tab count
    const browser = BrowserService.getInstance();
    const currentUrl = await getCurrentUrl(sessionId);
    const tabCount = await browser.getTabCount(sessionId);
    
    res.json({
      success: true,
      sessionId: sessionId,
      currentUrl: currentUrl,
      tabCount: tabCount,
      status: 'active',
      architecture: 'node-playwright-core',
      threadingIssues: 'resolved'
    });
    
  } catch (error) {
    console.error('❌ Failed to get browser status:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to get browser status'
    });
  }
});

// Take marked screenshot (with element highlighting)
app.post('/browser/screenshot-marked', async (req, res) => {
  try {
    const { sessionId, options = {} } = req.body;
    
    if (!sessionId) {
      return res.status(400).json({
        success: false,
        error: 'Session ID is required'
      });
    }
    
    if (!activeSessions.has(sessionId)) {
      return res.status(404).json({
        success: false,
        error: 'Session not found'
      });
    }
    
    console.log(`📸 Taking marked screenshot for session ${sessionId}`);
    
    // Get browser service instance
    const browser = BrowserService.getInstance();
    
    // Take marked screenshot with element highlighting
    const result = await browser.takeMarkedScreenshot(sessionId, {
      removeAfter: true,
      minWaitMs: 1000,
      ...options
    });
    
    console.log(`✅ Marked screenshot captured for session ${sessionId}`);
    
    res.json({
      type: 'marked_screenshot',
      success: true,
      image: result.image,
      elements: result.elements,
      sessionId: sessionId,
      timestamp: Date.now(),
      message: 'Marked screenshot captured successfully'
    });
    
  } catch (error) {
    console.error('❌ Failed to take marked screenshot:', error);
    res.status(500).json({
      type: 'error',
      success: false,
      error: error.message,
      message: 'Failed to capture marked screenshot'
    });
  }
});

// Close browser session
app.post('/browser/close', async (req, res) => {
  try {
    const { sessionId } = req.body;
    
    if (!sessionId) {
      return res.status(400).json({
        success: false,
        error: 'Session ID is required'
      });
    }
    
    console.log(`🔒 Closing browser session ${sessionId}`);
    
    // Close the browser session
    const browser = BrowserService.getInstance();
    await browser.closePage(sessionId);
    
    // Remove from active sessions
    activeSessions.delete(sessionId);
    
    console.log(`✅ Browser session ${sessionId} closed successfully`);
    
    res.json({
      success: true,
      sessionId: sessionId,
      message: 'Browser session closed successfully'
    });
    
  } catch (error) {
    console.error('❌ Failed to close browser session:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to close browser session'
    });
  }
});

// Click at coordinates
app.post('/browser/click', async (req, res) => {
  try {
    const { sessionId, x, y } = req.body;
    
    if (!sessionId || x === undefined || y === undefined) {
      return res.status(400).json({
        success: false,
        error: 'Session ID, x, and y coordinates are required'
      });
    }
    
    if (!activeSessions.has(sessionId)) {
      return res.status(404).json({
        success: false,
        error: 'Session not found'
      });
    }
    
    console.log(`👆 Clicking at coordinates (${x}, ${y}) for session ${sessionId}`);
    
    // Perform click - pass coordinates as object
    await click(sessionId, { x, y });
    
    console.log(`✅ Click performed successfully for session ${sessionId}`);
    
    res.json({
      success: true,
      sessionId: sessionId,
      x: x,
      y: y,
      message: 'Click performed successfully'
    });
    
  } catch (error) {
    console.error('❌ Click failed:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Click failed'
    });
  }
});

// Type text
app.post('/browser/type', async (req, res) => {
  try {
    const { sessionId, text } = req.body;
    
    if (!sessionId || text === undefined) {
      return res.status(400).json({
        success: false,
        error: 'Session ID and text are required'
      });
    }
    
    if (!activeSessions.has(sessionId)) {
      return res.status(404).json({
        success: false,
        error: 'Session not found'
      });
    }
    
    console.log(`⌨️ Typing text "${text}" for session ${sessionId}`);
    
    // Type text
    await type(sessionId, text);
    
    console.log(`✅ Text typed successfully for session ${sessionId}`);
    
    res.json({
      success: true,
      sessionId: sessionId,
      text: text,
      message: 'Text typed successfully'
    });
    
  } catch (error) {
    console.error('❌ Typing failed:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Typing failed'
    });
  }
});

// Scroll page
app.post('/browser/scroll', async (req, res) => {
  try {
    const { sessionId, direction = 'down', amount = 3 } = req.body;
    
    if (!sessionId) {
      return res.status(400).json({
        success: false,
        error: 'Session ID is required'
      });
    }
    
    if (!activeSessions.has(sessionId)) {
      return res.status(404).json({
        success: false,
        error: 'Session not found'
      });
    }
    
    if (!['up', 'down'].includes(direction)) {
      return res.status(400).json({
        success: false,
        error: 'Direction must be "up" or "down"'
      });
    }
    
    console.log(`📜 Scrolling ${direction} by ${amount} steps for session ${sessionId}`);
    
    // Get browser service instance
    const browser = BrowserService.getInstance();
    
    // Perform scroll using page.evaluate
    await browser.scroll(sessionId, direction, amount);
    
    console.log(`✅ Scroll performed successfully for session ${sessionId}`);
    
    res.json({
      success: true,
      sessionId: sessionId,
      direction: direction,
      amount: amount,
      message: 'Scroll performed successfully'
    });
    
  } catch (error) {
    console.error('❌ Scroll failed:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Scroll failed'
    });
  }
});

// Close all browser sessions
app.post('/browser/close-all', async (req, res) => {
  try {
    console.log('🔒 Closing all browser sessions');
    
    const browser = BrowserService.getInstance();
    await browser.closeAll();
    
    // Clear active sessions
    activeSessions.clear();
    
    console.log('✅ All browser sessions closed successfully');
    
    res.json({
      success: true,
      message: 'All browser sessions closed successfully'
    });
    
  } catch (error) {
    console.error('❌ Failed to close all browser sessions:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'Failed to close all browser sessions'
    });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('❌ Unhandled error:', err);
  res.status(500).json({
    success: false,
    error: err.message,
    message: 'Internal server error'
  });
});

// Start server
app.listen(PORT, () => {
  console.log('🚀 Browser Service Started');
  console.log('=' * 50);
  console.log(`📡 Server running on http://localhost:${PORT}`);
  console.log(`🎯 Architecture: Node.js + @presidio-dev/playwright-core`);
  console.log(`🔧 Threading Issues: Resolved ✅`);
  console.log(`📸 Vision Analysis: Ready`);
  console.log('=' * 50);
  
  // Handle graceful shutdown
  process.on('SIGINT', async () => {
    console.log('\n🔒 Shutting down browser service...');
    try {
      const browser = BrowserService.getInstance();
      await browser.closeAll();
      console.log('✅ All browser sessions closed');
    } catch (error) {
      console.error('❌ Error during shutdown:', error);
    }
    process.exit(0);
  });
});

// Export for testing
module.exports = app;
