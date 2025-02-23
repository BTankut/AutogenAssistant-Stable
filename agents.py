import json
import time
from typing import List, Dict, Any, Generator
from api import OpenRouterAPI

class Agent:
    def __init__(self, 
                 name: str, 
                 role: str, 
                 model: str, 
                 system_message: str):
        self.name = name
        self.role = role
        self.model = model
        self.system_message = system_message
        self.messages = [{"role": "system", "content": system_message}]
        self.start_time = None
        self.end_time = None

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def get_messages(self) -> List[Dict[str, str]]:
        return self.messages

    def start_processing(self):
        self.start_time = time.time()

    def end_processing(self):
        self.end_time = time.time()
        return self.end_time - self.start_time

class CoordinatorAgent(Agent):
    def __init__(self, name: str, model: str, system_message: str):
        super().__init__(name, "coordinator", model, system_message)

    def analyze_task(self, user_input: str, api: OpenRouterAPI) -> Dict[str, Any]:
        """Analyze user input to determine which agents should respond"""
        self.start_processing()

        analysis_prompt = f"""User message: {user_input}

        Analyze this message and determine which types of agents should respond.
        Response format: JSON with 'selected_roles' list and 'reasoning'"""

        self.add_message("user", analysis_prompt)
        response = api.generate_completion(
            model=self.model,
            messages=self.get_messages()
        )

        process_time = self.end_processing()

        if response["success"]:
            self.add_message("assistant", response["response"])
            try:
                return {
                    "success": True,
                    "analysis": response["response"],
                    "time": process_time
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to parse analysis: {str(e)}",
                    "time": process_time
                }
        else:
            return {
                "success": False,
                "error": response["error"],
                "time": process_time
            }

class AgentGroup:
    def __init__(self, api: OpenRouterAPI):
        self.api = api
        self.agents = {}
        self.coordinator = None
        self.response_cache = {}

    def add_agent(self, agent: Agent):
        if isinstance(agent, CoordinatorAgent):
            self.coordinator = agent
        else:
            self.agents[agent.name] = agent

    def remove_agent(self, agent_name: str):
        if agent_name in self.agents:
            del self.agents[agent_name]

    def get_response(self, agent_name: str) -> Dict[str, Any]:
        if agent_name not in self.agents:
            return {"success": False, "error": "Agent not found"}
            
        # Check cache first
        cache_key = f"{agent_name}_{str(self.agents[agent_name].messages)}"
        if cache_key in self.response_cache:
            return self.response_cache[cache_key]

        agent = self.agents[agent_name]
        agent.start_processing()
        response = self.api.generate_completion(
            model=agent.model,
            messages=agent.get_messages()
        )
        process_time = agent.end_processing()

        if response["success"]:
            response["time"] = process_time
            self.response_cache[cache_key] = response
            return response
        else:
            return response

    def get_collective_response(self, user_input: str) -> Generator[Dict[str, Any], None, None]:
        """Get coordinated responses from multiple agents, yielding intermediate results"""
        if not self.coordinator:
            yield {
                "success": False,
                "error": "No coordinator agent available"
            }
            return

        # Get task analysis from coordinator
        self.coordinator.start_processing()
        analysis = self.coordinator.analyze_task(user_input, self.api)
        coordinator_time = self.coordinator.end_processing()

        if not analysis["success"]:
            yield {
                **analysis,
                "coordinator_time": coordinator_time
            }
            return

        # Yield coordinator results first
        yield {
            "phase": "coordinator",
            "success": True,
            "analysis": analysis["analysis"],
            "coordinator_time": coordinator_time
        }

        responses = []
        total_tokens = 0
        agent_times = {}

        # Get responses from selected agents
        for agent_name, agent in self.agents.items():
            agent.start_processing()
            agent.add_message("user", user_input)
            response = self.get_response(agent_name)
            process_time = agent.end_processing()

            if response["success"]:
                agent_response = {
                    "agent": agent_name,
                    "response": response["response"],
                    "time": process_time
                }
                responses.append(agent_response)
                total_tokens += response["tokens"]
                agent_times[agent_name] = process_time

                # Yield intermediate result after each agent
                yield {
                    "phase": "agent_response",
                    "success": True,
                    "current_agent": agent_name,
                    "agent_response": agent_response,
                    "responses": responses,
                    "tokens": total_tokens,
                    "coordinator_analysis": analysis["analysis"],
                    "coordinator_time": coordinator_time,
                    "agent_times": agent_times,
                    "time": max(agent_times.values()) if agent_times else coordinator_time
                }

        try:
            # Get final evaluation from coordinator
            final_evaluation_prompt = f"""Here are all agent responses for the user input: {user_input}

            Agent responses:
            {json.dumps(responses, indent=2)}

            Please provide a final evaluation and synthesis of these responses.
            If the user is requesting code, you MUST include the final, optimized code implementation after your analysis.
            Your response should follow this format:

            1. Analysis: A clear, concise summary of the different approaches and their pros/cons
            2. Final Implementation: If code was requested, provide the complete, optimized code that combines the best aspects of all responses
            
            Make sure to include actual code, not just descriptions of what the code should do."""

            self.coordinator.add_message("user", final_evaluation_prompt)
            final_eval = self.api.generate_completion(
                model=self.coordinator.model,
                messages=self.coordinator.get_messages()
            )

            if final_eval["success"]:
                # Yield final complete result with coordinator's evaluation
                yield {
                    "phase": "complete",
                    "success": True,
                    "responses": responses,
                    "coordinator_analysis": analysis["analysis"],
                    "final_evaluation": final_eval["response"],
                    "tokens": total_tokens + final_eval.get("tokens", 0),
                    "coordinator_time": coordinator_time,
                    "agent_times": agent_times,
                    "time": max(agent_times.values()) if agent_times else coordinator_time
                }
            else:
                yield {
                    "phase": "complete",
                    "success": False,
                    "error": f"Final evaluation failed: {final_eval.get('error', 'Unknown error')}",
                    "responses": responses
                }
        except Exception as e:
            yield {
                "phase": "complete",
                "success": False,
                "error": f"Error in final evaluation: {str(e)}",
                "responses": responses
            }

    def get_agents(self) -> Dict[str, Agent]:
        return self.agents