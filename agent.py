"""Main agent implementation with conversation memory and tool support."""

from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from providers import LMStudioProvider
from config import Config
from tools import get_weather
import logging
from typing import List, Dict, Any
import uuid

logger = logging.getLogger(__name__)

class LangChainAgent:
    """Agent with tool support and conversation memory."""
    
    def __init__(self, provider: LMStudioProvider):
        """
        Initialize the agent with tools.
        
        Args:
            provider: LLM provider instance
        """
        self.provider = provider
        self.llm = provider.get_llm()
        
        # Initialize tools
        self.tools = [get_weather]
        
        # Initialize memory for conversation persistence
        self.memory = MemorySaver()
        self.thread_id = str(uuid.uuid4())
        
        # System prompt for the agent with tool guidance
        self.system_prompt = f"""You are {Config.AGENT_NAME}, a helpful AI assistant powered by LangChain.
You are running locally through LM Studio and have access to tools to help answer questions.

Available tools:
- get_weather: Get current weather information for any location

When users ask about weather, use the get_weather tool to provide accurate information.
Always be conversational, helpful, and concise in your responses.
If you don't have the right tool for a task, explain what you can and cannot do."""
        
        # Create the ReAct agent with tools
        self.agent = create_react_agent(
            self.llm, 
            self.tools, 
            prompt=self.system_prompt,
            checkpointer=self.memory
        )
        
        logger.info(f"Initialized {Config.AGENT_NAME} with {provider.get_provider_info()['name']} and {len(self.tools)} tools")
    
    def chat(self, user_input: str) -> str:
        """
        Process user input and return agent response using tools when needed.
        
        Args:
            user_input: User's message
            
        Returns:
            Agent's response
        """
        try:
            # Configuration for the agent execution
            config = {"configurable": {"thread_id": self.thread_id}}
            
            # Create input message
            input_message = HumanMessage(content=user_input)
            
            # Stream the agent execution to get the final response
            events = list(self.agent.stream(
                {"messages": [input_message]}, 
                config, 
                stream_mode="values"
            ))
            
            if events:
                # Get the last event which contains the final response
                final_event = events[-1]
                messages = final_event.get("messages", [])
                
                if messages:
                    # Find the last AI message
                    for msg in reversed(messages):
                        if isinstance(msg, AIMessage):
                            agent_response = msg.content
                            logger.info(f"Agent used tools and responded to: {user_input[:50]}...")
                            return agent_response
            
            # Fallback response if no proper response found
            return "I apologize, but I couldn't process your request properly."
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            logger.error(error_msg)
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get formatted conversation history from the agent's memory."""
        try:
            config = {"configurable": {"thread_id": self.thread_id}}
            
            # Get the current state from the agent's memory
            state = self.agent.get_state(config)
            messages = state.values.get("messages", [])
            
            history = []
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    history.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    history.append({"role": "assistant", "content": msg.content})
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def clear_memory(self):
        """Clear conversation memory by creating a new thread."""
        self.thread_id = str(uuid.uuid4())
        logger.info("Conversation memory cleared (new thread created)")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information including tools."""
        try:
            history = self.get_conversation_history()
            return {
                "name": Config.AGENT_NAME,
                "provider": self.provider.get_provider_info(),
                "memory_size": len(history),
                "system_prompt": self.system_prompt,
                "tools": [tool.name for tool in self.tools],
                "thread_id": self.thread_id
            }
        except Exception as e:
            logger.error(f"Error getting agent info: {e}")
            return {
                "name": Config.AGENT_NAME,
                "provider": self.provider.get_provider_info(),
                "error": str(e)
            }
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return [tool.name for tool in self.tools]
