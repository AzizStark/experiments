# LangChain Agent with LM Studio

A simple, extensible LangChain agent that works with LM Studio for local AI conversations. This project provides a minimal setup that can be easily extended to support additional providers like OpenAI and Claude, as well as tools, functions, and MCP integrations.

## Features

- 🤖 **Tool-Enabled Agent** - ReAct agent with weather tool support
- 🏠 **Local AI with LM Studio** - No API keys required for local models
- 🛠️ **Weather Tool** - Get weather information for any location
- 💾 **Conversation Memory** - Persistent memory across conversations
- 🔧 **Extensible Architecture** - Easy to add new providers and tools
- 📝 **Logging Support** - Comprehensive logging for debugging
- 🎯 **CLI Interface** - Simple command-line chat interface

## Prerequisites

1. **LM Studio** - Download and install from [lmstudio.ai](https://lmstudio.ai)
2. **Python 3.8+** - Make sure you have Python installed
3. **A Local Model** - Download and load a model in LM Studio

## Setup Instructions

### 1. LM Studio Setup

1. Download and install LM Studio
2. Download a model (e.g., Llama 2, Mistral, CodeLlama)
3. Load the model in LM Studio
4. Start the local server:
   - Go to "Local Server" tab in LM Studio
   - Click "Start Server"
   - Default URL: `http://localhost:1234`

### 2. Project Setup

1. **Clone/Download** this project
2. **Navigate** to the project directory:
   ```bash
   cd langchain-agent
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment** (optional):
   - Edit `.env` file to customize settings
   - Default settings should work with standard LM Studio setup

## Usage

### Start the Agent

```bash
python main.py
```

### Chat Commands

- **Regular chat**: Just type your message and press Enter
- **`/help`** - Show help message
- **`/info`** - Show agent and model information
- **`/history`** - Show conversation history
- **`/clear`** - Clear conversation memory
- **`/quit`** - Exit the application

### Example Conversation

```
🤖 Welcome to LangChain Agent!
============================================================
Powered by LangChain + LM Studio

✅ Agent ready! Start chatting...

You: Hello! How are you?
Agent: Hello! I'm doing well, thank you for asking. I'm your AI assistant running locally through LM Studio and powered by LangChain. How can I help you today?

You: What's the weather in New York?
Agent: 🌤️ Weather in New York:
• Condition: Partly Cloudy
• Temperature: 22°C
• Humidity: 65%
• Wind Speed: 12 km/h

You: How about London in fahrenheit?
Agent: 🌤️ Weather in London:
• Condition: Cloudy
• Temperature: 68°F
• Humidity: 78%
• Wind Speed: 8 km/h

You: /info
📊 Agent Information:
  Name: LangChain Agent
  Provider: LM Studio
  Model: local-model
  Base URL: http://localhost:1234/v1
  Memory Size: 6 messages
  Available Tools: get_weather
```

## Project Structure

```
langchain-agent/
├── .env                    # Environment configuration
├── requirements.txt        # Python dependencies
├── config.py              # Configuration settings
├── agent.py               # Main agent implementation
├── main.py                # CLI entry point
├── providers/             # Model providers (extensible)
│   ├── __init__.py
│   └── lm_studio.py       # LM Studio provider
├── tools/                 # Agent tools
│   ├── __init__.py
│   └── weather.py         # Weather tool implementation
└── README.md              # This file
```

## Configuration

Edit `.env` file to customize:

```env
# LM Studio Configuration
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_MODEL_NAME=local-model

# Agent Configuration
AGENT_NAME=LangChain Agent
MAX_TOKENS=2000
TEMPERATURE=0.7
```

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Ensure LM Studio is running
   - Check that a model is loaded
   - Verify the local server is started
   - Check the URL in `.env` matches LM Studio's server URL

2. **Import Errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

3. **Slow Responses**
   - Try a smaller model
   - Reduce `MAX_TOKENS` in `.env`
   - Check your system resources

### Logs

Check `agent.log` for detailed logging information.

## Future Extensions

This project is designed to be easily extensible:

### Adding New Providers

1. Create a new provider in `providers/` (e.g., `openai_provider.py`)
2. Implement the same interface as `LMStudioProvider`
3. Update `config.py` and `.env` with new provider settings
4. Modify `main.py` to support provider selection

### Adding Tools/Functions

1. Create a `tools/` directory
2. Implement LangChain tools
3. Modify `agent.py` to include tools in the agent

### Adding MCP Support

1. Install MCP dependencies
2. Create MCP client integration
3. Add MCP tools to the agent

## Dependencies

- **langchain** - Core LangChain framework
- **langchain-openai** - OpenAI-compatible API support (used for LM Studio)
- **langchain-community** - Community integrations
- **python-dotenv** - Environment variable management

## License

This project is open source. Feel free to modify and extend it for your needs!

## Contributing

This is a simple starter project. Feel free to:
- Add new features
- Improve error handling
- Add more providers
- Enhance the CLI interface
- Add web interface
- Integrate with other tools

Happy coding! 🚀
