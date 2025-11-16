from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any
import datetime
import logging


class Agent(ABC):
    """
    attributs:
    @name {str} - agent name
    @description {str}
    @options {Dict[str, Dict[str,Any]]} - agent spesific runtime options, use for expose to UI and user can configure agents (e.g. options = {"folder": {}, "dry_run": {}})
    """

    name: str = "BaseAgent"
    description: str = "Abstract base agent"
    
    # Optional runtime options for the agent (UI + planner support)
    options: Dict[str, Dict[str, Any]] = {}

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.last_run: Optional[datetime.datetime] = None
        self.last_result: Optional[Dict[str, Any]] = None
        self.status: str = "idle"
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        
        """
        Pre-agent file handler: logs for each agent which can feed to UI log viewer
        """
        fh = logging.FileHandler(f"logs/{self.name.lower()}.log")
        fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        self.logger.addHandler(fh)

    @abstractmethod
    async def run(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the agent logic with optional configuration.
        Should return structured result for logging, display, or chaining.
        """
        pass
    
    async def execute(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        execute() wraps run() for logging and status/error update
        """
        self.logger.info(f"Starting agent: {self.name}")
        self.status = "running"
        self.last_run = datetime.datetime.utcnow()

        try:
            result = await self.run(config)
            self.last_result = result
            self.status = "success"
            self.logger.info(f"{self.name} completed successfully.")
            return result
        except Exception as e:
            self.status = "error"
            self.last_result = {"error": str(e)}
            self.logger.error(f"{self.name} failed with error: {e}", exc_info=True)
            return self.last_result


    def get_metadata(self) -> Dict[str, Any]:
        """
        Returns basic metadata for UI or agent discovery.
        """
        return {
            "name": self.name,
            "description": self.description,
            "options": self.options,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "status": self.status
        }

