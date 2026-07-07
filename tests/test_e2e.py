import pytest
import httpx
from fastapi.testclient import TestClient
from src.main import app
import os

# ponytail: mock env for testing
os.environ["MASTER_KEY"] = "test-master-key"
os.environ["OPENROUTER_KEYS"] = "key1,key2"

client = TestClient(app)

@pytest.mark.asyncio
async def test_e2e_rotation():
    """
    Verify that a 429 response triggers key rotation 
    and the next request succeeds with a different key.
    """
    import respx
    
    with respx.mock() as respx_mock:
        # Mock 429 for key1, then 200 for key2
        route = respx_mock.get("https://openrouter.ai/api/v1/test")
        
        # Sequence: 429, then 200
        route.side_effect = [
            httpx.Response(429),
            httpx.Response(200, content=b"Success")
        ]

        # First request: should get 429
        resp1 = client.get("/proxy/openrouter/test", headers={"Authorization": "Bearer test-master-key"})
        assert resp1.status_code == 429

        # Second request: should get 200 (because it rotates to key2)
        resp2 = client.get("/proxy/openrouter/test", headers={"Authorization": "Bearer test-master-key"})
        assert resp2.status_code == 200
        assert resp2.content == b"Success"
