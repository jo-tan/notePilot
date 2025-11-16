from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from pathlib import Path
from agents.note_router import NoteRouterAgent
import settings

# --- 
# Brain Initialization
# ---
from brain.local_llm_brain import LocalLLMBrain

brain = LocalLLMBrain()

# ---
# Instantiate AgentManager
# ---
from managers.agent_manager import AgentManager
manager = AgentManager(brain)

# Register agents
note_router_agent = NoteRouterAgent(settings.ACTIVE_VAULT)
manager.register_agent(note_router_agent)



app = FastAPI(title="NotePilot Backend")

# --------- Models ---------
# To sanitize data at runtime. e.g. invalid data, missing fields, wrong type
class VaultSwitchRequest(BaseModel):
    vault_name: str

    # @validator("vault_name")
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("vault_name cannot be empty")
        return v

class BrainQueryRequest(BaseModel):
    prompt: str

class ExecuteRequest(BaseModel):
	instruction: str

# --------- Routes ---------

@app.get("/")
def index():
    return {"message": "NotePilot backend is running."}

@app.get("/health")
def health():
    return {"status": "ok",
			"active_vault": str(settings.ACTIVE_VAULT)
	}

@app.get("/get-vaults")
def get_vaults():
    return {"vaults": list(settings.VAULT_MAP.keys())}

@app.get("/active-vault")
def get_active_vault():
    return {"active_vault": str(settings.ACTIVE_VAULT)}

@app.post("/switch-vault")
def switch_vault(req: VaultSwitchRequest):
	try:
		settings.switch_active_vault(req.vault_name)
		return {
        	"message": f"Switched to vault '{req.vault_name}'",
        	"active_vault": settings.ACTIVE_VAULT_NAME,
			"path": str(settings.ACTIVE_VAULT)
    	}
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))

# --------- General ---------

@app.get("/agents/status")
def list_agent_statuses():
	return [
		agent.getmetadata()
		for agent in agent_registry.get_all()
	]

# --------- Specific Agent Calling ---------

@app.post("/run-note-router")
async def run_note_router(request: Request):
    body = await request.json()
    config = body.get("config", {})

    agent = NoteRouterAgent(settings.ACTIVE_VAULT)
    result = await agent.run(config=config)
    return result

# --------- Brain testing -----------

@app.get("/brain/test")
async def brain_test():
	result = await brain.plan_actions("clean up my notes")
	return result

@app.post("/brain/query")
def query_brain_endpoint(request: BrainQueryRequest):
    try:
        response = brain.query(request.prompt)
        return {"prompt": request.prompt, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --------- Agent Manager testing ---------
# Example FastAPI endpoint to plan + execute
@app.post("/agents/execute")
async def execute_instruction(req: ExecuteRequest):
    try:
        results = await manager.plan_and_execute(req.instruction)
        return {"instruction": req.instruction, "results": results}
    except Exception as e:
	    raise HTTPException(status_code=500, detail=str(e))
