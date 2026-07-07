import asyncio
from fastapi.testclient import TestClient
from src.main import app
from src.config import MASTER_KEY

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_proxy_no_auth():
    # Should fail with 401
    response = client.get("/proxy/openrouter/chat/completions")
    assert response.status_code == 401

def test_proxy_valid_auth():
    # Should not 401, but might 404 or 500 because we aren't actually hitting a real server with real keys yet
    # But it should pass the middleware
    headers = {"Authorization": f"Bearer {MASTER_KEY}"}
    response = client.get("/proxy/openrouter/chat/completions", headers=headers)
    # Since we use a mock key and fake URL, it'll probably fail inside proxy_request or via httpx, 
    # but if it's not 401, the middleware worked.
    assert response.status_code != 401

if __name__ == "__main__":
    test_root()
    test_proxy_no_auth()
    test_proxy_valid_auth()
    print("Basic infra checks passed!")
