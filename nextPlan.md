# NotePilot: Next Steps Plan

This document outlines the plan for the next phase of NotePilot development, focusing on creating a Textual TUI and implementing critical safety features.

## Phase 1: TUI Development and Safety Implementation

The goal is to build a functional, safe, and user-friendly interface for interacting with the NotePilot backend.

### Step 1: Project Scaffolding (The Foundation)

1.  **Create a New Directory:** In the project root, create a `tui/` directory to keep the TUI code separate from the `backend/`.
2.  **Set up a Virtual Environment:** Create and activate a new Python virtual environment inside the `tui/` directory.
3.  **Install Dependencies:** Install `textual` for the UI and `httpx` for asynchronous API calls.
    ```bash
    pip install textual httpx
    ```
4.  **Create the Entry Point:** Create a file `tui/main.py` to serve as the starting point for the Textual application.

### Step 2: The Basic Layout (Visual Skeleton)

1.  **Design the UI:** In `tui/main.py`, create a basic Textual `App`.
2.  **Add Widgets:** Use built-in widgets to create the main components:
    *   A `Header` for the application title.
    *   A `Log` or `RichLog` widget to display status updates and results.
    *   An `Input` widget for user commands.
    *   A `Footer` to show key bindings.
3.  **Goal:** At the end of this step, you should have a static, non-interactive layout when you run `python tui/main.py`.

### Step 3: Backend Communication (Connecting the Wires)

1.  **Fetch Status on Startup:** In the TUI's `on_mount` event, use `httpx` to make a `GET` request to the backend's `/health` or `/agents/status` endpoint.
2.  **Display Status:** Print the result of the API call to the `Log` widget to confirm the connection is working (e.g., "Connected to NotePilot backend.").

### Step 4: Implement the Safety Guardrail (Backend First)

This is a critical step to ensure the system operates safely. **This logic must be implemented in the backend.**

1.  **Modify `LocalLLMBrain`:** Open `backend/brain/local_llm_brain.py`.
2.  **Create a Safety Check Method:** Implement a private method like `_is_prompt_safe(self, prompt: str)` that checks for high-risk keywords (e.g., "ip address", "mac address", "delete files", "execute command").
3.  **Apply the Check:** In the `query` method, call the safety check *before* sending the prompt to the Ollama API.
4.  **Decline Unsafe Prompts:** If the prompt is deemed unsafe, return a polite, hardcoded refusal message.
5.  **Test:** Restart the backend and use the API docs or `curl` to test the `/brain/query` endpoint with a dangerous prompt to ensure it is blocked.

### Step 5: Implement Command Execution and Chat

1.  **Handle Input:** In the TUI, add an event handler for when the user submits the `Input` widget.
2.  **Differentiate Commands:**
    *   If the input starts with a prefix like `/chat `, send the rest of the text to the `/brain/query` endpoint.
    *   Otherwise, treat the input as an instruction for the `AgentManager` and `POST` it to the `/agents/execute` endpoint.
3.  **Display Results:** Format the JSON response from the backend and print it to the `Log` widget.

### Step 6: Add a Simple Menu

1.  **Create a Menu Widget:** Use a `Static` or `Select` widget.
2.  **Populate with Actions:** Hardcode a few common actions (e.g., "Clean up my notes", "Chat with Brain").
3.  **Link to Input:** When a user selects a menu item, it should pre-fill the `Input` widget with the corresponding command.

---

## Phase 2: Professional Prompt and Safety Management

This phase refines the initial hard-coded safety implementation into a scalable, professional approach by externalizing configuration. This is a best practice for maintainability.

### Key Concept: Prompt Templating vs. RAG

*   **Prompt Templating / Externalized Configuration:** This is the practice of storing prompts, configurations, and safety rules in external files (like YAML or JSON) instead of hard-coding them in the application. The application loads these files at runtime. This is what we will use for our safety rules.
*   **Retrieval-Augmented Generation (RAG):** This is a more advanced technique where the system first *retrieves* relevant information from a knowledge base (e.g., your notes) and then adds that information to the prompt as context for the LLM. It's used to give the LLM knowledge it wasn't trained on.

### Step 1: Create an External Configuration File

1.  **Create a `prompts` directory** inside `backend/`.
2.  **Create a YAML file:** Inside `backend/prompts`, create `safety_config.yaml`.
3.  **Define rules and prompts** in this file.

    ```yaml
    # backend/prompts/safety_config.yaml

    # The message returned when a prompt is blocked.
    polite_refusal: "I'm sorry, but I cannot process that request as it seems to ask for sensitive information or to perform a restricted action."

    # List of keywords that will trigger the safety guardrail.
    # The check will be case-insensitive.
    blocked_keywords:
      - "ip address"
      - "mac address"
      - "system information"
      - "environment variables"
      - "delete files"
      - "execute command"
      - "os.system"
      - "subprocess.run"
      - "what is my password"
      - "show my screen"
      - "access my camera"
    ```

### Step 2: Modify the Backend to Load the Configuration

1.  **Add Dependency:** Add `PyYAML` to your `backend/requirements.txt` and install it.
2.  **Update `LocalLLMBrain`:** Modify the brain to load and use the `safety_config.yaml` file at startup.

    ```python
    # In backend/brain/local_llm_brain.py
    import yaml
    from pathlib import Path

    class LocalLLMBrain(Brain):
        def __init__(self):
            super().__init__()
            # ... other initializations ...

            # --- Load Safety Configuration ---
            config_path = Path(__file__).parent.parent / "prompts" / "safety_config.yaml"
            with open(config_path, 'r') as f:
                safety_config = yaml.safe_load(f)
            
            self.polite_refusal = safety_config['polite_refusal']
            self.blocked_keywords = safety_config['blocked_keywords']

        def _is_prompt_safe(self, prompt: str) -> bool:
            lower_prompt = prompt.lower()
            if any(keyword in lower_prompt for keyword in self.blocked_keywords):
                print(f"Blocked potentially unsafe prompt: '{prompt}'")
                return False
            return True

        def query(self, prompt: str) -> str:
            if not self._is_prompt_safe(prompt):
                return self.polite_refusal
            
            # ... rest of the query logic ...
    ```

### Benefits of This Approach

*   **Maintainability:** Safety rules and prompts can be updated by editing the YAML file, with no code changes required.
*   **Readability:** The rules are stored in a clear, human-readable format.
*   **Scalability:** This same file can be expanded to hold system prompts for the `AgentManager` and other configurations, keeping all LLM-related instructions in one organized place.