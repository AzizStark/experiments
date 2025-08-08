"""Main agent implementation with conversation memory."""

from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage
from langchain_core.messages import HumanMessage, AIMessage
from providers import LMStudioProvider
from config import Config
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class LangChainAgent:
    """Simple conversational agent with memory support."""
    
    def __init__(self, provider: LMStudioProvider):
        """
        Initialize the agent.
        
        Args:
            provider: LLM provider instance
        """
        self.provider = provider
        self.llm = provider.get_llm()
        
        # Initialize conversation memory
        self.memory = ConversationBufferWindowMemory(
            k=10,  # Keep last 10 exchanges
            return_messages=True,
            memory_key=Config.MEMORY_KEY
        )
        
        # System prompt for the agent
        self.system_prompt = f"""You are {Config.AGENT_NAME}, a helpful AI assistant. 
You are running locally through LM Studio and powered by LangChain.
Be conversational, helpful, and concise in your responses.
If you don't know something, just say so honestly."""
        
        logger.info(f"Initialized {Config.AGENT_NAME} with {provider.get_provider_info()['name']}")
    
    def chat(self, user_input: str) -> str:
        """
        Process user input and return agent response.
        
        Args:
            user_input: User's message
            
        Returns:
            Agent's response
        """
        try:
            # Get conversation history
            history = self.memory.chat_memory.messages
            
            # Prepare messages for the LLM
            messages = []
            
            # Add system message if this is the first interaction
            if not history:
                messages.append(("system", self.system_prompt))
            
            # Add conversation history
            for msg in history:
                if isinstance(msg, HumanMessage):
                    messages.append(("human", msg.content))
                elif isinstance(msg, AIMessage):
                    messages.append(("assistant", msg.content))
            
            # Add current user input
            messages.append(("human", user_input))
            
            # Get response from LLM
            response = self.llm.invoke(messages)
            
            # Extract content from response
            if hasattr(response, 'content'):
                agent_response = response.content
            else:
                agent_response = str(response)
            
            # Save to memory
            self.memory.chat_memory.add_user_message(user_input)
            self.memory.chat_memory.add_ai_message(agent_response)
            
            logger.info(f"Processed user input: {user_input[:50]}...")
            return agent_response
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            logger.error(error_msg)
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get formatted conversation history."""
        history = []
        for msg in self.memory.chat_memory.messages:
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                history.append({"role": "assistant", "content": msg.content})
        return history
    
    def clear_memory(self):
        """Clear conversation memory."""
        self.memory.clear()
        logger.info("Conversation memory cleared")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            "name": Config.AGENT_NAME,
            "provider": self.provider.get_provider_info(),
            "memory_size": len(self.memory.chat_memory.messages),
            "system_prompt": self.system_prompt
        }
