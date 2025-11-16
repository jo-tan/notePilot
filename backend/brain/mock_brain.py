# backend/brain/mock_brain.py
from .base import Brain

class MockBrain(Brain):
    name = "MockBrain"
    description = "Simple mock brain for testing pipelines."

    async def analyze(self, user_input: str):
        return {"intent": "mock_intent", "message": f"You said: {user_input}"}

    async def plan_actions(self, user_input: str):
        plan = {
            "plan": [
                {"tool": "checkVaultPath"},
                {"tool": "runNoteRouterAgent", "args": {"folder": "99-TBD"}}
            ]
        }
        self.record_run(plan)
        return plan

