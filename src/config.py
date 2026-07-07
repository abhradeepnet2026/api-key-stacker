import os
from itertools import cycle
from dotenv import load_dotenv

load_dotenv()

MASTER_KEY = os.getenv("MASTER_KEY")
PORT = int(os.getenv("PORT", 8000))

# ponytail: simple map for base URLs
PROVIDER_CONFIG = {
    "openrouter": "https://openrouter.ai/api/v1",
    "nvidia": "https://integrate.api.nvidia.com/v1",
    "ollama": "https://ollama.com/api",
    "zai": "https://api.z.ai/v1",
    "google": "https://generativelanguage.googleapis.com/v1beta",
    "xai": "https://api.x.ai/v1",
}

class KeyPool:
    """Rotates through a comma-separated list of API keys."""
    def __init__(self, keys_str: str):
        self.keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        self._cycle = cycle(self.keys) if self.keys else None

    def get_next(self):
        return next(self._cycle) if self._cycle else None

    def __len__(self):
        return len(self.keys)

if __name__ == "__main__":
    # ponytail: minimal self-check for rotation logic
    pool = KeyPool("key1,key2,key3")
    results = [pool.get_next() for _ in range(5)]
    assert results == ["key1", "key2", "key3", "key1", "key2"]
    print("KeyPool rotation verified.")
