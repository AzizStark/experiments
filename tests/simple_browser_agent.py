"""
Simple Browser Agent with Vision
CLI-style browser automation with automatic vision feedback after each action.
"""

import sys
import os
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver

# Import our simple CLI-style browser tools
from tools.browser_vision_tools import (
    launch,
    navigate,
    click,
    type_text,
    scroll,
    look,
    close,
    status,
    check_health
)

logger = logging.getLogger(__name__)

class SimpleBrowserAgent:
    """Simple browser automation agent with vision capabilities."""
    
    def __init__(self, model_name: str = "qwen2-vl-2b-instruct"):
        """Initialize the browser agent."""
        self.model_name = model_name
        self.llm = self._initialize_llm()
        self.tools = self._get_tools()
        self.checkpointer = InMemorySaver()
        self.agent = self._create_agent()
        
    def _initialize_llm(self) -> ChatOpenAI:
        """Initialize the language model."""
        return ChatOpenAI(
            base_url="http://localhost:1234/v1",
            api_key="lm-studio",
            model=self.model_name,
            temperature=0.1
        )
    
    def _get_tools(self) -> list:
        """Get the list of simple browser tools."""
        return [
            launch,
            navigate, 
            click,
            type_text,
            scroll,
            look,
            close,
            status
        ]
    
    def _create_agent(self):
        """Create the ReAct agent with browser tools."""
        
        system_prompt = """You are a browser automation agent with vision capabilities. After each action you take, you will automatically see what happened on the screen through vision analysis.

Available tools:
- launch(url): Launch browser and go to URL (always use this first)
- navigate(url): Navigate to a new URL  
- click(x, y): Click at coordinates x,y
- type_text(text): Type text into focused element
- scroll(direction, amount): Scroll page ('up' or 'down', amount=steps)
- look(): Take screenshot and analyze current screen
- status(): Check browser session status
- close(): Close browser session

Key features:
- After EVERY action (launch, navigate, click, type, scroll), you automatically get vision analysis
- You can see what changed, what's on screen, and what interactive elements are available
- Use this visual feedback to guide your next actions
- Coordinates for clicking: screen is typically 900x600, click in center of elements
- Always launch() first before any other actions

Instructions:
1. Plan your approach step by step
2. Use launch() to start
3. After each action, read the vision analysis carefully  
4. Use the visual feedback to decide next steps
5. Look for submit buttons to click rather than using keyboard shortcuts
6. Be specific about what you're trying to accomplish
7. Close browser when task is complete

You excel at web automation tasks like form filling, navigation, data extraction, and web interaction."""

        # Create ReAct agent
        return create_react_agent(
            self.llm,
            self.tools,
            prompt=system_prompt,
            checkpointer=self.checkpointer
        )
    
    def run_task(self, task: str, thread_id: str = "default") -> str:
        """Run a browser automation task."""
        try:
            logger.info(f"Starting browser task: {task}")
            
            config = {"configurable": {"thread_id": thread_id}}
            input_message = {"messages": [{"role": "user", "content": task}]}
            
            # Execute the agent
            result = self.agent.invoke(input_message, config)
            
            # Extract final response
            final_messages = result.get("messages", [])
            if final_messages:
                for msg in reversed(final_messages):
                    if hasattr(msg, 'content') and hasattr(msg, 'type'):
                        if msg.type == 'ai':  # AIMessage
                            return msg.content
            
            return "Task completed, but no final response found."
            
        except Exception as e:
            error_msg = f"Task execution failed: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def stream_task(self, task: str, thread_id: str = "default"):
        """Stream the execution of a browser task."""
        try:
            config = {"configurable": {"thread_id": thread_id}}
            input_message = {"messages": [{"role": "user", "content": task}]}
            
            for chunk in self.agent.stream(input_message, config, stream_mode="values"):
                yield chunk
                
        except Exception as e:
            yield {"error": str(e)}
    
    def check_health(self):
        """Check if all systems are ready."""
        return check_health()

def test_amazon_navigation():
    """Test navigating to Amazon and analyzing the page."""
    print("🤖 Testing Simple Browser Agent - Amazon Navigation")
    print("=" * 60)
    
    agent = SimpleBrowserAgent()
    
    # Check system health
    print("🔍 Checking system health...")
    health = agent.check_health()
    print(f"Browser Service: {'✅' if health['browser_service']['healthy'] else '❌'}")
    print(f"Vision Model: {'✅' if health['vision_model']['healthy'] else '❌'}")
    
    if not health['overall_healthy']:
        print("⚠️ System not ready. Please ensure:")
        print("1. Browser service: cd browser-service && npm start")
        print("2. LM Studio with Qwen-2.5-VL on localhost:1234")
        return False
    
    print("\n🚀 System ready! Starting browser task...")
    
    task = """1. Navigate to saucedemo.com
2. find the username input and click on it at coordinates {"x":639,"y":176}
3. then type standard_user as username
4. find password input and click on it at coordinates {"x":640,"y":228}
5. then type secret_sauce as password
6. then click on submit button at  (640, 328)"""

    print(f"\n📋 Task: {task}")
    print("\n" + "="*60)
    print("🔄 Agent Execution:")
    print("="*60)
    
    try:
        result = agent.run_task(task)
        print(f"\n📋 Final Result:\n{result}")
        return True
        
    except Exception as e:
        print(f"\n❌ Task failed: {e}")
        return False

def test_google_search():
    """Test performing a Google search."""
    print("\n🤖 Testing Google Search")
    print("=" * 50)
    
    agent = SimpleBrowserAgent()
    
    task = """Please search for "artificial intelligence" on Google:

1. Launch browser and go to google.com
2. Find the search box and click on it
3. Type "artificial intelligence" 
4. Click search or press enter (look for search button)
5. Tell me what search results you see
6. Close browser when done

Describe what you see after each step."""

    print(f"Task: {task}")
    print("\nExecuting...")
    
    try:
        result = agent.run_task(task)
        print(f"\n📋 Result:\n{result}")
        return True
    except Exception as e:
        print(f"\n❌ Task failed: {e}")
        return False

def test_streaming_execution():
    """Test streaming execution to see step-by-step progress."""
    print("\n🤖 Testing Streaming Execution")
    print("=" * 50)
    
    agent = SimpleBrowserAgent()
    
    task = "Go to github.com and tell me what you see on the homepage"
    
    print(f"Task: {task}")
    print("\nStreaming execution...")
    
    try:
        step_count = 0
        for chunk in agent.stream_task(task):
            if "error" in chunk:
                print(f"❌ Error: {chunk['error']}")
                break
            
            messages = chunk.get("messages", [])
            if messages:
                last_message = messages[-1]
                if hasattr(last_message, 'type'):
                    if last_message.type == 'ai':
                        step_count += 1
                        print(f"\n🤖 Agent Step {step_count}:")
                        print("-" * 30)
                        content = last_message.content[:150] + "..." if len(last_message.content) > 150 else last_message.content
                        print(content)
                    elif last_message.type == 'tool':
                        tool_name = getattr(last_message, 'name', 'unknown')
                        print(f"\n🛠️ Tool: {tool_name}")
                        content = last_message.content[:200] + "..." if len(last_message.content) > 200 else last_message.content
                        print(content)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Streaming failed: {e}")
        return False

def main():
    """Run all tests for the simple browser agent."""
    print("🎯 Simple Browser Agent with Vision")
    print("=" * 60)
    print("CLI-style browser automation with automatic vision feedback")
    print("=" * 60)
    
    tests = [
        ("Amazon Navigation Test", test_amazon_navigation)
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
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    successful_tests = sum(1 for passed in results.values() if passed)
    total_tests = len(results)
    
    print(f"\n🎯 Overall: {successful_tests}/{total_tests} tests passed")
    
    if successful_tests > 0:
        print("\n💡 Simple Browser Agent Features:")
        print("✅ CLI-style tool names (launch, navigate, click, type, scroll)")
        print("✅ Automatic vision analysis after every action")
        print("✅ Visual feedback guides next actions")
        print("✅ Simple ReAct pattern implementation")
        print("✅ Easy to use for local models")
        
        print("\n🚀 Usage Example:")
        print("agent = SimpleBrowserAgent()")
        print('result = agent.run_task("Go to amazon.com and find the search box")')
        
    else:
        print("\n⚠️ Tests failed. Check setup:")  
        print("1. Browser service: cd browser-service && npm start")
        print("2. LM Studio with Qwen-2.5-VL on localhost:1234")

if __name__ == "__main__":
    main()
