from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse
import httpx
from src.config import MASTER_KEY
from src.key_pool import get_pool

app = FastAPI()

# ponytail: mapping of provider to base URL
PROVIDERS = {
    "openrouter": "https://openrouter.ai/api/v1",
    "nvidia": "https://nv-ai.nvidia.com",
    "ollama": "https://ollama-cloud.com",
    "zai": "https://z.ai/api",
    "google": "https://generativelanguage.googleapis.com",
    "xai": "https://api.x.ai",
}

async def verify_master_key(request: Request):
    auth = request.headers.get("Authorization")
    if auth != f"Bearer {MASTER_KEY}":
        raise HTTPException(status_code=401, detail="Invalid Master Key")

async def proxy_request(provider: str, path: str, request: Request):
    if provider not in PROVIDERS:
        raise HTTPException(status_code=404, detail="Provider not found")

    pool = get_pool(provider)
    key = await pool.get_key()
    
    url = f"{PROVIDERS[provider]}/{path}"
    
    # Forward headers, replace Authorization with the pooled key
    headers = dict(request.headers)
    headers["Authorization"] = f"Bearer {key}"
    headers.pop("host", None)

    async with httpx.AsyncClient() as client:
        # ponytail: stream response for efficiency
        # Use a standard request instead of stream() for the skeleton to avoid closure issues with StreamingResponse in tests
        resp = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=await request.body(),
            params=request.query_params,
        )
        
        # Handle key rotation on 401/429
        if resp.status_code in (401, 429):
            await pool.rotate(key)
        
        return StreamingResponse(
            iter([resp.content]),
            status_code=resp.status_code,
            headers=dict(resp.headers)
        )

@app.get("/")
async def root():
    return {"status": "ok"}

@app.api_route("/proxy/{provider}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], dependencies=[Depends(verify_master_key)])
async def proxy_handler(provider: str, path: str, request: Request):
    return await proxy_request(provider, path, request)
