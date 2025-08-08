"""Configuration settings for the LangChain Agent."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the agent."""
    
    # LM Studio Configuration
    LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
    LM_STUDIO_MODEL_NAME = os.getenv("LM_STUDIO_MODEL_NAME", "local-model")
    
    # Future provider configurations
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # Agent Configuration
    AGENT_NAME = os.getenv("AGENT_NAME", "LangChain Agent")
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Memory Configuration
    MEMORY_KEY = "chat_history"
    INPUT_KEY = "input"
    OUTPUT_KEY = "output"
