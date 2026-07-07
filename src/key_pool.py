import os
from itertools import cycle
from typing import Dict

class KeyPool:
    """Rotates through API keys for a specific provider."""
    def __init__(self, provider: str):
        self.provider = provider.upper()
        # ponytail: keys are stored as PROVIDER_KEYS in env
        keys_str = os.getenv(f"{self.provider}_KEYS", "")
        self.keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        self._cycle = cycle(self.keys) if self.keys else None

    async def get_key(self) -> str:
        if not self._cycle:
            return "NO_KEYS_CONFIGURED"
        return next(self._cycle)

    async def rotate(self, key: str):
        # In a simple cycle, get_key already rotates.
        pass

# Global pool cache to avoid re-initializing on every request
_pools: Dict[str, KeyPool] = {}

def get_pool(provider: str) -> KeyPool:
    if provider not in _pools:
        _pools[provider] = KeyPool(provider)
    return _pools[provider]
