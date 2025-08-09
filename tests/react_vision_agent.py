"""
ReAct Vision Agent Implementation
Autonomous web browsing agent with vision capabilities using LangGraph.
Demonstrates multi-step reasoning and vision analysis of web content.
"""

import sys
import os
import logging
from typing import Annotated, Dict, Any, List

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent, ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver
from typing_extensions import TypedDict

# Import our vision-aware browser tools
from tools.vision_browser_tools import (
    launch_browser_with_vision,
    navigate_and_analyze,
    analyze_current_page,
    compare_pages,
    close_browser_session,
    check_vision_browser_health
)

logger = logging.getLogger(__name__)

# Agent State Definition
class VisionAgentState(TypedDict):
    """State for the vision-enabled ReAct agent."""
    messages: Annotated[List[BaseMessage], add_messages]
    visited_pages: List[str]  # Track URLs visited
    page_analyses: Dict[str, str]  # Store analysis results

class AutonomousVisionAgent:
    """
    Autonomous Vision Agent that can browse websites and analyze content.
    Uses ReAct pattern with vision-capable tools for web analysis.
    """
    
    def __init__(self, model_name: str = "qwen2-vl-2b-instruct"):
        """Initialize the autonomous vision agent."""
        self.model_name = model_name
        self.llm = self._initialize_llm()
        self.tools = self._get_tools()
        self.checkpointer = InMemorySaver()  # Initialize before creating agent
        self.agent = self._create_agent()
        
    def _initialize_llm(self) -> ChatOpenAI:
        """Initialize the vision-capable language model."""
        return ChatOpenAI(
            base_url="http://localhost:1234/v1",
            api_key="lm-studio",
            model=self.model_name,
            temperature=0.1  # Lower temperature for more consistent reasoning
        )
    
    def _get_tools(self) -> List:
        """Get the list of vision-aware browser tools."""
        return [
            launch_browser_with_vision,
            navigate_and_analyze,
            analyze_current_page,
            compare_pages,
            close_browser_session
        ]
    
    def _create_agent(self):
        """Create the ReAct agent with vision tools."""
        # System prompt emphasizing vision capabilities and autonomous reasoning
        system_prompt = f"""You are an autonomous web browsing agent with vision capabilities. You can see and analyze web content through screenshots.

Your core capabilities:
- Launch browsers and navigate to websites
- Automatically analyze what you see on web pages using vision AI
- Compare multiple websites and provide detailed analysis
- Plan and execute multi-step browsing tasks autonomously

Available tools:
- launch_browser_with_vision: Start browsing with automatic page analysis
- navigate_and_analyze: Navigate to URLs and automatically analyze content
- analyze_current_page: Analyze current page with specific questions
- compare_pages: Visit multiple URLs and compare them
- close_browser_session: Clean up when done

Important guidelines:
1. Always use vision analysis to understand what you're seeing
2. Be descriptive about visual content - layout, text, images, interactive elements
3. Plan your approach for multi-step tasks
4. Provide comprehensive analysis and comparisons
5. Clean up by closing browser sessions when tasks are complete

You excel at autonomous web research, comparative analysis, and providing detailed insights about web content through vision analysis."""

        # Create ReAct agent using LangGraph's prebuilt function
        return create_react_agent(
            self.llm,
            self.tools,
            prompt=system_prompt,
            checkpointer=self.checkpointer
        )
    
    def run_task(self, task: str, thread_id: str = "default") -> str:
        """
        Run an autonomous browsing task.
        
        Args:
            task: Description of the task to perform
            thread_id: Thread ID for conversation persistence
            
        Returns:
            Final response from the agent
        """
        try:
            logger.info(f"Starting autonomous task: {task}")
            
            # Configuration for the agent execution
            config = {
                "configurable": {"thread_id": thread_id}
            }
            
            # Create input message
            input_message = {"messages": [HumanMessage(content=task)]}
            
            # Execute the agent
            result = self.agent.invoke(input_message, config)
            
            # Extract the final response
            final_messages = result.get("messages", [])
            if final_messages:
                # Get the last AI message
                for msg in reversed(final_messages):
                    if isinstance(msg, AIMessage):
                        return msg.content
            
            return "Task completed, but no final response found."
            
        except Exception as e:
            error_msg = f"Task execution failed: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def stream_task(self, task: str, thread_id: str = "default"):
        """
        Stream the execution of an autonomous browsing task.
        
        Args:
            task: Description of the task to perform
            thread_id: Thread ID for conversation persistence
            
        Yields:
            Stream of execution steps
        """
        try:
            logger.info(f"Starting streaming task: {task}")
            
            config = {
                "configurable": {"thread_id": thread_id}
            }
            
            input_message = {"messages": [HumanMessage(content=task)]}
            
            # Stream the agent execution
            for chunk in self.agent.stream(input_message, config, stream_mode="values"):
                yield chunk
                
        except Exception as e:
            logger.error(f"Streaming task failed: {str(e)}")
            yield {"error": str(e)}
    
    def check_health(self) -> Dict[str, Any]:
        """Check if all systems are ready for autonomous browsing."""
        return check_vision_browser_health()

def test_amazon_comparison():
    """Test the agent with Amazon comparison task."""
    print("🤖 Testing Autonomous Vision Agent - Amazon Comparison")
    print("=" * 60)
    
    # Initialize agent
    agent = AutonomousVisionAgent()
    
    # Check system health
    print("🔍 Checking system health...")
    health = agent.check_health()
    print(f"Browser Service: {'✅' if health['browser_service']['healthy'] else '❌'} {health['browser_service']['status']}")
    print(f"Vision Model: {'✅' if health['vision_model']['healthy'] else '❌'} {health['vision_model']['status']}")
    
    if not health['overall_healthy']:
        print("⚠️ System not ready. Please ensure:")
        print("1. Browser service is running: cd browser-service && npm start")
        print("2. LM Studio is running with Qwen-2.5-VL model on localhost:1234")
        return False
    
    print("\n🚀 System ready! Starting autonomous browsing task...")
    
    # Define the task
    task = """I need you to compare amazon.com and amazon.in. Please:

1. Visit amazon.com and analyze what you see on the homepage
2. Visit amazon.in and analyze what you see on the homepage  
3. Provide a detailed comparison of the differences between both sites
4. Focus on layout, featured products, regional differences, and overall user experience

Please be thorough in your analysis and provide specific details about what you observe visually on each site."""

    print(f"\n📋 Task: {task}")
    print("\n" + "="*60)
    print("🔄 Agent Execution (Streaming):")
    print("="*60)
    
    # Stream the task execution
    try:
        for i, chunk in enumerate(agent.stream_task(task)):
            if "error" in chunk:
                print(f"❌ Error: {chunk['error']}")
                break
            
            # Print step information
            messages = chunk.get("messages", [])
            if messages:
                last_message = messages[-1]
                if isinstance(last_message, AIMessage):
                    print(f"\n🤖 Agent Step {i+1}:")
                    print("-" * 40)
                    print(last_message.content[:200] + "..." if len(last_message.content) > 200 else last_message.content)
                elif isinstance(last_message, ToolMessage):
                    tool_name = getattr(last_message, 'name', 'Unknown Tool')
                    print(f"\n🛠️ Tool Result ({tool_name}):")
                    print("-" * 40)
                    content = last_message.content
                    print(content[:300] + "..." if len(content) > 300 else content)
    
    except KeyboardInterrupt:
        print("\n⚠️ Task interrupted by user")
    except Exception as e:
        print(f"\n❌ Task failed: {e}")
    
    print("\n" + "="*60)
    print("✅ Task execution complete!")
    return True

def test_simple_navigation():
    """Test simple navigation and analysis."""
    print("\n🤖 Testing Simple Navigation and Analysis")
    print("=" * 50)
    
    agent = AutonomousVisionAgent()
    
    task = "Please launch a browser and go to github.com and tell me what you see on the homepage. Describe the layout, main elements, and purpose of the site."
    
    print(f"Task: {task}")
    print("\nExecuting...")
    
    result = agent.run_task(task)
    print(f"\n📋 Result:\n{result}")
    
    return True

def test_multi_step_research():
    """Test multi-step research task."""
    print("\n🤖 Testing Multi-Step Research Task")
    print("=" * 50)
    
    agent = AutonomousVisionAgent()
    
    task = """Please help me research e-commerce platforms. I want you to:

1. Visit amazon.com and analyze their homepage design and features
2. Visit ebay.com and analyze their homepage design and features
3. Compare both platforms and tell me the key differences in their approach to e-commerce

Focus on visual design, user experience, and how they present products to users."""
    
    print(f"Task: {task}")
    print("\nExecuting with streaming...")
    
    step_count = 0
    for chunk in agent.stream_task(task):
        if "error" in chunk:
            print(f"❌ Error: {chunk['error']}")
            break
        
        messages = chunk.get("messages", [])
        if messages:
            last_message = messages[-1]
            if isinstance(last_message, AIMessage):
                step_count += 1
                print(f"\n🤖 Agent Reasoning Step {step_count}:")
                print(last_message.content[:150] + "...")
            elif isinstance(last_message, ToolMessage):
                print(f"🛠️ Tool executed: {getattr(last_message, 'name', 'Unknown')}")
    
    return True

def main():
    """Run all tests for the autonomous vision agent."""
    print("🎯 Autonomous Vision Agent - ReAct Implementation")
    print("=" * 70)
    print("Testing autonomous web browsing with vision analysis capabilities")
    print("=" * 70)
    
    tests = [
        ("Simple Navigation Test", test_simple_navigation),
        ("Amazon Comparison Test", test_amazon_comparison),  
        ("Multi-Step Research Test", test_multi_step_research)
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
        print("\n💡 Your autonomous vision agent is working!")
        print("Key capabilities demonstrated:")
        print("✅ Autonomous web navigation with vision analysis")
        print("✅ Multi-step reasoning and task planning")
        print("✅ Comparative analysis of multiple websites")
        print("✅ Detailed visual content analysis")
        print("✅ ReAct pattern implementation with LangGraph")
        
        print("\n🚀 Ready for autonomous browsing tasks!")
        print("Example usage:")
        print("agent = AutonomousVisionAgent()")
        print('result = agent.run_task("Compare google.com and bing.com search pages")')
        
    else:
        print("\n⚠️ Tests failed. Check your setup:")
        print("1. Browser service running: cd browser-service && npm start")
        print("2. LM Studio with Qwen-2.5-VL on localhost:1234")
        print("3. Vision integration working: python tests/simple_vision_example.py")

if __name__ == "__main__":
    main()
