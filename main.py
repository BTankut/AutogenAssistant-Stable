import streamlit as st
import json
from config import DEFAULT_AGENT_ROLES, init_session_state
from api import OpenRouterAPI
from agents import Agent, CoordinatorAgent, AgentGroup
from utils import format_conversation, create_metrics_charts, update_metrics
import os
from dotenv import load_dotenv

# Page configuration
st.set_page_config(
    page_title="Multi-Agent Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Error handling wrapper
def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return None
    return wrapper

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Initialize session state
if 'messages' not in st.session_state:
    init_session_state()

# Sidebar
with st.sidebar:
    st.title("🤖 Agent Configuration")

    # Use API key from environment
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        st.session_state.api_key = api_key
        api = OpenRouterAPI(api_key)

        # Fetch available models
        models_response = api.get_models()
        if models_response["success"]:
            available_models = {
                model["id"]: model["id"]
                for model in models_response["models"]
            }
            st.session_state.available_models = available_models

            # Load saved model selections if they exist
            try:
                with open('.model_selections.json', 'r') as f:
                    saved_models = json.load(f)
                    st.session_state.selected_models = saved_models
            except FileNotFoundError:
                if 'selected_models' not in st.session_state:
                    st.session_state.selected_models = {
                        'coordinator': None,
                        'user_proxy': None,
                        'coder': None,
                        'critic': None
                    }
        else:
            st.error("Failed to fetch models from OpenRouter")
            st.session_state.available_models = {}

        # Initialize AgentGroup if not exists
        if 'agent_group' not in st.session_state:
            st.session_state.agent_group = AgentGroup(api)

        # Coordinator setup
        if not st.session_state.coordinator:
            st.subheader("Setup Coordinator")
            if st.session_state.available_models:
                # Get saved coordinator model or default to first
                default_coordinator_model = st.session_state.selected_models.get('coordinator')
                default_index = 0
                if default_coordinator_model in st.session_state.available_models:
                    default_index = list(st.session_state.available_models.keys()).index(default_coordinator_model)

                coordinator_model = st.selectbox(
                    "Coordinator Model",
                    list(st.session_state.available_models.keys()),
                    key="coordinator_model",
                    index=default_index
                )

                if st.button("Setup Coordinator"):
                    coordinator = CoordinatorAgent(
                        name="Coordinator",
                        model=st.session_state.available_models[coordinator_model],
                        system_message=DEFAULT_AGENT_ROLES["coordinator"]["system_message"]
                    )
                    st.session_state.agent_group.add_agent(coordinator)
                    st.session_state.coordinator = coordinator
                    # Save selected model
                    st.session_state.selected_models['coordinator'] = coordinator_model
                    # Save to file
                    with open('.model_selections.json', 'w') as f:
                        json.dump(st.session_state.selected_models, f)
                    st.success("Coordinator agent setup successfully!")

        # Agent creation
        st.subheader("Create New Agent")

        # Show roles with descriptions
        roles = [role for role in DEFAULT_AGENT_ROLES.keys() if role != "coordinator"]

        agent_role = st.selectbox(
            "Role",
            roles,
            format_func=lambda x: f"{DEFAULT_AGENT_ROLES[x]['name']}: {DEFAULT_AGENT_ROLES[x]['description']}"
        )

        if st.session_state.available_models:
            # Get saved model for this role or default to first
            default_model = st.session_state.selected_models.get(agent_role)
            default_index = 0
            if default_model in st.session_state.available_models:
                default_index = list(st.session_state.available_models.keys()).index(default_model)

            agent_model = st.selectbox(
                "Model",
                list(st.session_state.available_models.keys()),
                index=default_index
            )

            if st.button("Add Agent"):
                role_config = DEFAULT_AGENT_ROLES[agent_role]
                new_agent = Agent(
                    name=role_config["name"],
                    role=agent_role,
                    model=st.session_state.available_models[agent_model],
                    system_message=role_config["system_message"]
                )
                st.session_state.agent_group.add_agent(new_agent)
                st.session_state.current_agents.append(role_config["name"])
                # Save selected model
                st.session_state.selected_models[agent_role] = agent_model
                # Save to file
                with open('.model_selections.json', 'w') as f:
                    json.dump(st.session_state.selected_models, f)
                st.success(f"Agent {role_config['name']} added successfully!")
        else:
            st.warning("No models available. Please check your API key.")

# Main content
st.title("Multi-Agent Dashboard")

if not st.session_state.api_key:
    st.warning("Please enter your OpenRouter API key in the sidebar.")
else:
    # Create tabs
    tab1, tab2 = st.tabs(["Chat", "Metrics"])

    with tab1:
        # Chat interface
        st.subheader("Agent Conversation")

        if 'agent_group' in st.session_state:
            agents = st.session_state.agent_group.get_agents()

            if agents:
                # Chat mode selection and Reset Chat button in the same row
                col1, col2 = st.columns([3, 1])
                with col1:
                    chat_mode = st.radio(
                        "Chat Mode",
                        ["Single Agent", "Collective (Coordinated)"],
                        horizontal=True
                    )
                with col2:
                    if st.button("🔄 Reset Chat", help="Start a new chat while keeping agent configurations"):
                        # Clear conversation history
                        st.session_state.conversations = []

                        # Reset all agent messages to their initial system messages
                        for agent_name, agent in st.session_state.agent_group.get_agents().items():
                            agent.messages = [{"role": "system", "content": agent.system_message}]

                        # Reset coordinator messages if exists
                        if st.session_state.coordinator:
                            st.session_state.coordinator.messages = [
                                {"role": "system", "content": st.session_state.coordinator.system_message}
                            ]

                        # Clear any active user inputs
                        if 'user_input' in st.session_state:
                            del st.session_state.user_input

                        # Force the UI to refresh
                        st.rerun()

                # Display available agents
                st.subheader("Available Agents")

                # First display coordinator if exists
                if st.session_state.coordinator:
                    st.write(f"• **{st.session_state.coordinator.name}** ({st.session_state.coordinator.model})")

                # Then display other agents
                for agent_name, agent in agents.items():
                    st.write(f"• **{agent_name}** ({agent.model})")

                # Message input
                user_input = st.text_area("Your message")

                if chat_mode == "Single Agent":
                    selected_agent = st.selectbox(
                        "Select agent to respond",
                        list(agents.keys())
                    )

                    if st.button("Send"):
                        if user_input:
                            # Add user message
                            agents[selected_agent].add_message("user", user_input)

                            # Get agent response
                            response = st.session_state.agent_group.get_response(
                                selected_agent
                            )

                            if response["success"]:
                                # Add agent response
                                agents[selected_agent].add_message(
                                    "assistant",
                                    response["response"]
                                )

                                # Update metrics
                                update_metrics(
                                    st.session_state.metrics,
                                    response,
                                    agents[selected_agent].model
                                )

                                # Save conversation
                                st.session_state.conversations.append({
                                    "mode": "single",
                                    "agent": selected_agent,
                                    "messages": agents[selected_agent].get_messages()
                                })
                            else:
                                st.error(f"Error: {response['error']}")

                else:  # Collective mode
                    if not st.session_state.coordinator:
                        st.warning("Please set up a coordinator agent first.")
                    else:
                        if st.button("Send to All"):
                            if user_input:
                                # Create a main container for all progress indicators
                                main_container = st.container()

                                # Overall progress
                                progress_placeholder = st.empty()
                                progress_bar = st.progress(0)

                                # Individual agent progress indicators
                                agent_progress = {}
                                for agent_name in st.session_state.agent_group.get_agents().keys():
                                    agent_progress[agent_name] = st.empty()

                                # Create placeholders for responses
                                coordinator_analysis_placeholder = st.empty()
                                agent_responses_container = st.container()

                                with main_container:
                                    try:
                                        # Initialize metrics
                                        total_tokens = 0
                                        responses = []

                                        # Get collective response generator
                                        response_generator = st.session_state.agent_group.get_collective_response(user_input)

                                        for response in response_generator:
                                            if not response["success"]:
                                                st.error(f"Error: {response.get('error', 'Unknown error')}")
                                                progress_bar.empty()
                                                break

                                            if response["phase"] == "coordinator":
                                                # Step 1: Coordinator Analysis (0-40%)
                                                progress_placeholder.write("🔄 Analyzing input...")
                                                progress_bar.progress(30)

                                                with coordinator_analysis_placeholder:
                                                    with st.expander("🔍 Detailed Analysis", expanded=False):
                                                        st.markdown(response["analysis"])
                                                progress_bar.progress(40)

                                            elif response["phase"] == "agent_response":
                                                # Update progress based on completed responses
                                                total_agents = len(st.session_state.agent_group.get_agents())
                                                completed_agents = len(response["responses"])
                                                progress = 40 + (completed_agents / total_agents * 50)

                                                # Update progress message
                                                progress_placeholder.write(f"🤖 Getting agent responses... ({completed_agents}/{total_agents})")

                                                # Update progress bar
                                                progress_bar.progress(int(progress))

                                                # Collect responses
                                                responses.append(response["agent_response"])

                                            elif response["phase"] == "complete":
                                                # Final Processing (90-100%)
                                                progress_placeholder.write("✨ Finalizing...")
                                                progress_bar.progress(95)

                                                # Show coordinator's final evaluation first
                                                st.success("✅ Process completed!")
                                                st.write("**Coordinator's Final Evaluation:**")
                                                st.write(response["final_evaluation"])

                                                # Show detailed responses in collapsed expander
                                                with st.expander("🔍 Detailed Agent Responses", expanded=False):
                                                    for resp in responses:
                                                        st.write(f"\n**{resp['agent']}** response:")
                                                        st.write(resp["response"])

                                                # Show metrics in collapsed expander
                                                with st.expander("📊 Performance Metrics", expanded=False):
                                                    st.write(f"Total tokens: {response['tokens']}")
                                                    st.write(f"Total time: {response['time']:.2f} seconds")

                                                progress_bar.progress(100)

                                                # Update metrics
                                                update_metrics(
                                                    st.session_state.metrics,
                                                    {
                                                        "success": True,
                                                        "tokens": response["tokens"],
                                                        "time": response["time"]
                                                    },
                                                    "collective"
                                                )

                                                # Save conversation
                                                st.session_state.conversations.append({
                                                    "mode": "collective",
                                                    "user_input": user_input,
                                                    "coordinator_analysis": response["coordinator_analysis"],
                                                    "responses": response["responses"]
                                                })

                                    except Exception as e:
                                        st.error(f"An error occurred: {str(e)}")
                                        progress_bar.empty()

                # Display conversation history
                st.subheader("Conversation History")
                for conv in st.session_state.conversations:
                    if conv["mode"] == "single":
                        with st.expander(f"Single Agent Conversation with {conv['agent']}"):
                            st.markdown(format_conversation(conv['messages']))
                    else:
                        with st.expander("Collective Conversation"):
                            st.write("**User**:", conv["user_input"])
                            st.write("\n**Coordinator Analysis**:", conv["coordinator_analysis"])
                            for resp in conv["responses"]:
                                st.write(f"\n**{resp['agent']}**:", resp["response"])
            else:
                st.info("Add agents using the sidebar to start chatting!")

    with tab2:
        # Metrics display
        st.subheader("Performance Metrics")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Tokens Used", st.session_state.metrics['total_tokens'])
        with col2:
            if st.session_state.metrics['response_times']:
                avg_time = sum(st.session_state.metrics['response_times']) / \
                          len(st.session_state.metrics['response_times'])
                st.metric("Average Response Time (s)", f"{avg_time:.2f}")

        # Display charts
        create_metrics_charts(st.session_state.metrics)
