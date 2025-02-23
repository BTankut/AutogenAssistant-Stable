
# Multi-Agent Dashboard with OpenRouter Integration

A comprehensive dashboard for managing and interacting with multiple AI agents using OpenRouter API. This application provides a streamlined interface for coordinated AI interactions with advanced configuration options and real-time progress tracking.

## 🌟 Features

### Core Functionality
- **Multi-Agent System**: Coordinate multiple AI agents with different roles and capabilities
- **Model Persistence**: Automatically saves and loads model selections for each agent role
- **Dynamic Model Selection**: Choose from available OpenRouter models for each agent
- **Coordinated Chain Responses**: Sequential agent interactions orchestrated by a coordinator
- **Real-time Progress Tracking**: Visual feedback on processing status and agent responses

### User Interface
- **Interactive Chat Interface**: Easy-to-use chat interface for both single and collective agent interactions
- **Collapsible Views**: Expandable sections for detailed analysis and responses
- **Performance Metrics**: Track token usage and response times
- **Visual Analytics**: Charts and graphs for performance monitoring

### Agent Types
- **Coordinator**: Orchestrates task distribution and synthesizes final responses
- **Human Assistant**: Represents user interests and handles natural language tasks
- **Code Assistant**: Specializes in programming and technical implementation
- **Critic**: Provides analysis and quality assessment

## 🚀 Getting Started

### Prerequisites
- Python 3.11
- OpenRouter API key

### Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
```bash
OPENROUTER_API_KEY=your_api_key_here
```

4. Run the application:
```bash
streamlit run main.py
```

## 💡 Usage Guide

### Setting Up Agents

1. **Configure Coordinator**:
   - Select preferred model from available OpenRouter models
   - Model selection is automatically saved for future sessions
   - Click "Setup Coordinator" to initialize

2. **Add Specialized Agents**:
   - Choose agent role (Human Assistant, Code Assistant, Critic)
   - Select model from available options
   - Model selections persist between sessions
   - Click "Add Agent" to create

### Chat Modes

1. **Single Agent Mode**:
   - Direct interaction with specific agent
   - Utilizes agent's specialized capabilities
   - View individual responses

2. **Collective Mode**:
   - Chain-based interaction with all configured agents
   - Coordinator analyzes and distributes tasks
   - Real-time progress tracking
   - Synthesized final response

### Performance Monitoring

- Track token usage per interaction
- Monitor response times
- View model distribution analytics
- Access detailed agent performance metrics

## 🔐 Security

- Secure API key management
- Environment variable configuration
- No data persistence for sensitive information

## 📝 Notes

- Model selections are automatically saved in `.model_selections.json`
- Reset chat functionality maintains agent configurations
- Real-time progress tracking shows chain execution status

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
