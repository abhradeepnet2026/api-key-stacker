import os
from dotenv import load_dotenv

load_dotenv()

MASTER_KEY = os.getenv("MASTER_KEY")
PORT = int(os.getenv("PORT", 8000))

# ponytail: single source of truth for base URLs
PROVIDER_CONFIG = {
    "openrouter": "https://openrouter.ai/api/v1",
    "nvidia": "https://integrate.api.nvidia.com/v1",
    "ollama": "https://ollama.com/api",
    "zai": "https://api.z.ai/v1",
    "google": "https://generativelanguage.googleapis.com/v1beta",
    "xai": "https://api.x.ai/v1",
}
