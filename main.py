"""Main entry point for the LangChain Agent."""

import logging
import sys
from typing import Optional
try:
    from agent import LangChainAgent
    LANGGRAPH_AVAILABLE = True
except ImportError:
    from agent_simple import SimpleLangChainAgent as LangChainAgent
    LANGGRAPH_AVAILABLE = False
from providers import LMStudioProvider
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def create_agent() -> Optional[LangChainAgent]:
    """Create and initialize the agent."""
    try:
        # Initialize LM Studio provider
        provider = LMStudioProvider(
            base_url=Config.LM_STUDIO_BASE_URL,
            model_name=Config.LM_STUDIO_MODEL_NAME,
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS
        )
        
        # Test connection
        logger.info("Testing connection to LM Studio...")
        if not provider.test_connection():
            logger.error("Failed to connect to LM Studio. Please ensure:")
            logger.error("1. LM Studio is running")
            logger.error("2. A model is loaded")
            logger.error("3. Local server is started (default: http://localhost:1234)")
            return None
        
        # Create agent
        agent = LangChainAgent(provider)
        logger.info("Agent initialized successfully!")
        return agent
        
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        return None

def print_welcome():
    """Print welcome message."""
    print("\n" + "="*60)
    print(f"🤖 Welcome to {Config.AGENT_NAME}!")
    print("="*60)
    print("Powered by LangChain + LM Studio")
    print("\nCommands:")
    print("  /help    - Show this help message")
    print("  /info    - Show agent information")
    print("  /history - Show conversation history")
    print("  /clear   - Clear conversation memory")
    print("  /quit    - Exit the application")
    print("\nStart chatting by typing your message!")
    print("="*60 + "\n")

def print_help():
    """Print help message."""
    print("\n📖 Help:")
    print("  Just type your message and press Enter to chat!")
    print("  Use commands starting with '/' for special actions.")
    print("  The agent remembers the last 10 exchanges for context.\n")

def main():
    """Main application loop."""
    print_welcome()
    
    # Create agent
    agent = create_agent()
    if not agent:
        print("❌ Failed to initialize agent. Exiting...")
        sys.exit(1)
    
    print("✅ Agent ready! Start chatting...\n")
    
    # Main chat loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith('/'):
                command = user_input.lower()
                
                if command == '/quit' or command == '/exit':
                    print("\n👋 Goodbye!")
                    break
                
                elif command == '/help':
                    print_help()
                    continue
                
                elif command == '/info':
                    info = agent.get_agent_info()
                    print(f"\n📊 Agent Information:")
                    print(f"  Name: {info['name']}")
                    print(f"  Provider: {info['provider']['name']}")
                    print(f"  Model: {info['provider']['model']}")
                    print(f"  Base URL: {info['provider']['base_url']}")
                    print(f"  Memory Size: {info['memory_size']} messages")
                    if 'tools' in info:
                        print(f"  Available Tools: {', '.join(info['tools'])}")
                    print()
                    continue
                
                elif command == '/history':
                    history = agent.get_conversation_history()
                    if not history:
                        print("\n📝 No conversation history yet.\n")
                    else:
                        print(f"\n📝 Conversation History ({len(history)} messages):")
                        for i, msg in enumerate(history, 1):
                            role = "You" if msg["role"] == "user" else "Agent"
                            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                            print(f"  {i}. {role}: {content}")
                        print()
                    continue
                
                elif command == '/clear':
                    agent.clear_memory()
                    print("\n🧹 Conversation memory cleared!\n")
                    continue
                
                else:
                    print(f"\n❓ Unknown command: {user_input}")
                    print("Type '/help' for available commands.\n")
                    continue
            
            # Process chat message
            print("Agent: ", end="", flush=True)
            response = agent.chat(user_input)
            print(response + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"\n❌ An error occurred: {e}\n")

if __name__ == "__main__":
    main()
