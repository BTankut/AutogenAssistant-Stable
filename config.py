import streamlit as st

# Default agent roles
DEFAULT_AGENT_ROLES = {
    "coordinator": {
        "name": "Coordinator",
        "description": "Coordinates and manages other agents",
        "system_message": """You are a coordinator agent responsible for:
1. Analyzing user messages
2. Determining which specialized agents should respond
3. Combining and summarizing agent responses
4. Ensuring coherent multi-agent conversations

Always explain your reasoning when delegating tasks to agents."""
    },
    "user_proxy": {
        "name": "Human Assistant",
        "description": "Represents the user's interests and manages task delegation",
        "system_message": "You are a helpful assistant representing the user's interests."
    },
    "coder": {
        "name": "Code Assistant",
        "description": "Specialized in writing and reviewing code",
        "system_message": "You are an expert programmer focused on writing clean, efficient code."
    },
    "critic": {
        "name": "Critic",
        "description": "Reviews and provides constructive feedback",
        "system_message": "You are a thoughtful critic who provides detailed analysis and feedback."
    }
}

def init_session_state():
    """Initialize session state variables"""
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    if 'conversations' not in st.session_state:
        st.session_state.conversations = []
    if 'current_agents' not in st.session_state:
        st.session_state.current_agents = []
    if 'metrics' not in st.session_state:
        st.session_state.metrics = {
            'total_tokens': 0,
            'response_times': [],
            'model_usage': {}
        }
    if 'available_models' not in st.session_state:
        st.session_state.available_models = {}
    if 'coordinator' not in st.session_state:
        st.session_state.coordinator = None

    # Remember selected models for each role
    if 'selected_models' not in st.session_state:
        st.session_state.selected_models = {
            'coordinator': None,
            'user_proxy': None,
            'coder': None,
            'critic': None
        }