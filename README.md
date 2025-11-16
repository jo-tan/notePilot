# NotePilot

NotePilot is an AI-powered agent designed to manage and organize Obsidian notes. It uses a local Large Language Model (LLM) to understand the content of your notes and then deploys various agents to perform tasks like cleaning, tagging, and sorting notes into relevant directories.

## Current Features

*   **FastAPI Backend:** A robust backend powered by FastAPI, providing a stable API for agent interaction and management.
*   **Local LLM Integration:** Utilizes a local LLM (e.g., Ollama with `gemma2:2b`) to interpret natural language commands and generate action plans.
*   **Agent-Based Architecture:** A modular, agent-based system that allows for the easy addition of new functionalities.
*   **Vault Management:** Supports multiple Obsidian vaults and allows for easy switching between them.
*   **Note Router Agent:** A built-in agent that moves unorganized Markdown files from the root of your vault to a designated folder.
*   **Docker Support:** Includes a `Dockerfile` and `docker-compose.yml` for easy containerized deployment.

## Project Structure

```
notePilot/
├── .env                  # Environment variables for configuration
├── docker-compose.yml    # Docker Compose for service orchestration
├── backend/
│   ├── Dockerfile          # Dockerfile for the backend service
│   ├── main.py             # FastAPI application entry point
│   ├── requirements.txt    # Python dependencies
│   ├── settings.py         # Application settings and vault management
│   ├── agents/             # Contains the different agents
│   │   ├── base.py         # Base agent class
│   │   └── note_router.py  # Agent for routing notes
│   ├── brain/              # Handles LLM interaction
│   │   ├── base.py         # Base brain class
│   │   └── local_llm_brain.py # Implementation for local LLM
│   └── managers/
│       └── agent_manager.py # Orchestrates agents and the brain
└── logs/
    └── noterouteragent.log # Log file for the Note Router Agent
```

## Getting Started

### Prerequisites

*   Python 3.8+
*   Docker and Docker Compose
*   An Ollama-compatible local LLM (e.g., `gemma2:2b`)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd notePilot
    ```

2.  **Set up the environment:**
    Create a `.env` file in the root of the project and add the following variables:
    ```
    DEFAULT_VAULT=personal
    VAULT_PERSONAL=/path/to/your/personal/vault
    VAULT_WORK=/path/to/your/work/vault
    OLLAMA_MODEL=gemma2:2b
    OLLAMA_HOST=http://host.docker.internal:11434
    ```

3.  **Build and run the services:**
    ```bash
    docker-compose up --build
    ```

4.  **Access the API:**
    The FastAPI backend will be available at `http://localhost:8000`. You can access the API documentation at `http://localhost:8000/docs`.

## Future Plans

*   **More Agents:** Develop additional agents for tasks like:
    *   **Tagger Agent:** Automatically adds tags to notes based on their content.
    *   **Archiver Agent:** Moves old or irrelevant notes to an archive folder.
    *   **Linker Agent:** Suggests links between related notes.
*   **Text-Based User Interface (TUI):** Create a TUI for interacting with the NotePilot agents and monitoring their status.
*   **React Flow Visualization:** Implement a React Flow-based UI to visualize the status of the agents and the workflow, similar to n8n.
*   **Improved Brain:** Enhance the `LocalLLMBrain` to better understand complex commands and generate more sophisticated action plans.
*   **Agent Tool List:** Create a dynamic tool list of available agents that the orchestrator can use to perform actions.
