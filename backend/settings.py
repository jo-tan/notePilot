from pathlib import Path
import os

# Load default vault name
DEFAULT_VAULT_NAME = os.getenv("DEFAULT_VAULT")
if not DEFAULT_VAULT_NAME:
    raise RuntimeError("❌ DEFAULT_VAULT is not set in .env")

# Dynamically load all VAULT_ keys
VAULT_MAP = {}
for key, value in os.environ.items():
    if key.startswith("VAULT_"):
        vault_name = key.removeprefix("VAULT_")
        VAULT_MAP[vault_name] = Path(value)

ACTIVE_VAULT_NAME = DEFAULT_VAULT_NAME
ACTIVE_VAULT = VAULT_MAP[ACTIVE_VAULT_NAME]

# (Optional) Debug
print(f"✅ ACTIVE_VAULT = {DEFAULT_VAULT_NAME} → {ACTIVE_VAULT}")

def switch_active_vault(vault_name: str):
    global ACTIVE_VAULT_NAME, ACTIVE_VAULT
    if vault_name not in VAULT_MAP:
        raise ValueError(f"Vault '{vault_name}' not in available vaults: {list(VAULT_MAP)}")
    ACTIVE_VAULT_NAME = vault_name
    ACTIVE_VAULT = VAULT_MAP[vault_name]
    print(f"✅ Switched active vault to: {ACTIVE_VAULT_NAME} → {ACTIVE_VAULT}")
