from typing import Dict, List, Any
from agents.base import Agent
from brain.local_llm_brain import LocalLLMBrain

class AgentManager:
    """
    Manages all registered agents and coordinates with the Brain.
    """

    def __init__(self, brain: LocalLLMBrain):
        self.brain = brain
        self.agents: Dict[str, Agent] = {}

    def register_agent(self, agent: Agent):
        self.agents[agent.name] = agent

    def get_status(self) -> List[Dict[str, Any]]:
        return [agent.get_metadata() for agent in self.agents.values()]

    async def run_agent(self, name: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        agent = self.agents.get(name)
        if not agent:
            raise ValueError(f"Agent '{name}' not found")
        result = await agent.run(config)
        return result

    async def plan_and_execute(self, instruction: str) -> Dict[str, Any]:
        """"
        Use Brain to generate a structured JSON plan, then execute each agent.
        """
        system_prompt = (
            "You are a planner that translates natural language instructions "
            "into a JSON plan for automation agents.\n"
            "Respond ONLY with valid JSON and no explanations.\n"
            "Example format:\n"
            "{\n"
            '  "steps": [\n'
            '    {"agent": "NoteRouterAgent", "config": {"target_folder": "99-TBD"}},\n'
            '    {"agent": "TaggerAgent", "config": {"tags": ["review"]}}\n'
            "  ]\n"
            "}\n\n"
            f"Instruction: {instruction}"
        )
        print("\n🧠 [AgentManager] Sending to brain:\n", system_prompt)
        response = self.brain.query(system_prompt)
        print("\n🤖 [Brain raw response]:\n", response)
        
        # Here we assume the brain returns JSON-like structure(Not Ready)
        import json
        import re

        response = self.brain.query(system_prompt)

        # Clean Markdown fences or other wrappers
        cleaned = re.sub(r"^```(?:json)?|```$", "", response.strip(), flags=re.MULTILINE).strip()

        try:
            plan = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse brain response as JSON: {e}\nRaw output:\n{response}")
        # --- Execute each step ---
        results = []
        for step in plan.get("steps", []):
            agent_name = step["agent"]
            config = step.get("config", {})
            print(f"\n🚀 Executing agent: {agent_name} with config {config}")
            result = await self.run_agent(agent_name, config)
            results.append({agent_name: result})

        return {
            "instruction": instruction,
            "raw_response": response,
            "parsed_plan": plan,
            "results": results
        }

