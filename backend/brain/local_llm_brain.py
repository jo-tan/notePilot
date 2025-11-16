# backend/brain/local_llm_brain.py
from .base import Brain
import json
import os
import requests
from typing import Any, Dict

class LocalLLMBrain(Brain):
    """
    A local LLM-powered brain that interprets user input
    and generates structured action plans by making API calls to an Ollama service.
    """

    name = "LocalLLMBrain"
    description = "Uses a local LLM (e.g. gemma2:2b) to plan agent actions."

    def __init__(self):
        super().__init__()
        self.model_name = os.getenv("OLLAMA_MODEL", "gemma2:2b")
        # Get the Ollama host from environment variables, with a fallback for local dev
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    def query(self, prompt: str) -> str:
        """
        Sends a prompt to the Ollama API and returns the response.
        """
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False  # We want the full response at once
                },
                headers={"Content-Type": "application/json"}
            )
            # Raise an exception if the request failed
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except requests.exceptions.RequestException as e:
            # Handle connection errors, timeouts, etc.
            raise RuntimeError(f"LLM API Error: {e}")

    async def analyze(self, user_input: str) -> Dict[str, Any]:
        """
        Interpret user input using the local LLM.
        """
        prompt = f"Analyze the following user input and determine the intent and entities: '{user_input}'"
        response = self.query(prompt)
        # This is a placeholder. In a real scenario, you'd parse the LLM response.
        return {"intent": "llm_analyzed", "raw_response": response}

    async def plan_actions(self, user_input: str) -> Dict[str, Any]:
        """
        Generate a plan of actions using the local LLM.
        """
        example = {
            "plan": [
                {"tool": "runNoteRouterAgent"}
            ]
        }
        example_json = json.dumps(example)
        prompt = f"Based on the user input '{user_input}', create a JSON plan of actions. Example: {example_json}"
        response_str = self.query(prompt)
        try:
            # Attempt to parse the LLM's response as JSON
            plan = json.loads(response_str)
        except json.JSONDecodeError:
            # If parsing fails, return a default plan with the raw response
            plan = {"plan": [], "error": "Failed to parse LLM response", "raw_response": response_str}
        
        self.record_run(plan)
        return plan
