from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import datetime

class Brain(ABC):
    name: str = "BaseBrain"
    description: str = "Abstract reasoning brian"

    def __init__(self):
        # Time and result tracking (for UI / logging)
        self.last_run: Optional[datetime.datetime] = None
        self.last_result: Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------
    # Core abstract methods — all subclasses must implement these
    # ------------------------------------------------------------

    @abstractmethod
    async def analyze(self, user_input: str) -> Dict[str,Any]:
        """
        Interpret a natural-language user command and return a structured
        response — e.g. intent, context, or suggested actions.

        Example return value:
        {
            "intent": "cleanup_notes",
            "vault": "local",
            "actions": [
                {"tool": "checkVaultPath"},
                {"tool": "switchVault", "args": {"target": "local"}},
                {"tool": "runNoteRouterAgent"}
            ]
        }
        """
        pass
    
    @abstractmethod
    async def plan_actions(self, user_input: str) -> Dict[str, Any]:
        """
        Convert the interpreted input into a structured execution plan
        suitable for the AgentManager.

        Example return:
        {
            "plan": [
                {"tool": "checkVaultPath"},
                {"tool": "switchVault", "args": {"target": "local"}},
                {"tool": "runNoteRouterAgent"}
            ]
        }
        """
        pass

    # ---------------------------
    # Optional utility methods for sharesd functionality
    # --------------------------

    def record_run(self, result: Dict[str, Any]) -> None:
        """Store metadata about the lastest run."""
        self.last_run = datetime.datetime.now()
        self.last_result = result

    def get_metadata(self) -> Dict[str, Any]:
        """Basic info for UI, logs, or health checks"""
        return {
            "name": self.name,
            "description": self.description,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "last_result": self.last_result,
        }

    def query(self, prompt: str) -> str:
        """accept natural language prompt and return a response"""
        pass

