from agents.base import Agent
from pathlib import Path
from typing import Optional, Dict, List
import shutil
import settings
import datetime


class NoteRouterAgent(Agent):
    name = "NoteRouterAgent"
    description = "Moves markdown files from the vault root to a designated folder (e.g. '99 - TBD')."
    options = {
        "target_folder_name": {
            "type": "string",
            "default": "99 - TBD",
            "description": "The folder to move unorganized notes into"
        }
    }

    def __init__(self, vault_path: Path):
        super().__init__(vault_path)
        self.last_run: Optional[datetime.datetime] = None
        self.last_result: Optional[Dict] = None

    async def run(self, config: Optional[Dict] = None) -> Dict:
        config = config or {}

        target_folder_name = config.get(
            "target_folder_name", self.options["target_folder_name"]["default"]
        )

        target_folder = self.vault_path / target_folder_name
        target_folder.mkdir(exist_ok=True)

        root_notes: List[str] = []
        moved_notes: List[str] = []

        for note in self.vault_path.glob("*.md"):
            root_notes.append(note.name)
            destination = target_folder / note.name
            shutil.move(str(note), str(destination))
            moved_notes.append(note.name)

        result = {
            "status": "done",
            "timestamp": datetime.datetime.now().isoformat(),
            "target_folder": target_folder_name,
            "total_found": len(root_notes),
            "total_moved": len(moved_notes),
            "moved_files": moved_notes
        }

        # Track state internally
        self.last_run = datetime.datetime.now()
        self.last_result = result

        return result

