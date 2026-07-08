from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse
import httpx
from src.config import MASTER_KEY, PROVIDER_CONFIG
from src.key_pool import get_pool

app = FastAPI()

# ponytail: global client for connection pooling (huge perf gain)
client = httpx.AsyncClient(timeout=httpx.Timeout(60.0))

async def verify_master_key(request: Request):
    auth = request.headers.get("Authorization")
    if auth != f"Bearer {MASTER_KEY}":
        raise HTTPException(status_code=401, detail="Invalid Master Key")

async def proxy_request(provider: str, path: str, request: Request):
    if provider not in PROVIDER_CONFIG:
        raise HTTPException(status_code=404, detail="Provider not found")

    pool = get_pool(provider)
    key = await pool.get_key()
    body = await request.body()
    resp = await perform_request(provider, key, path, request, body, pool)
    
    return StreamingResponse(
        resp.aiter_raw(),
        status_code=resp.status_code,
        headers=dict(resp.headers)
    )

async def perform_request(provider: str, key: str, path: str, request: Request, body: bytes, pool=None):
    url = f"{PROVIDER_CONFIG[provider]}/{path}"
    headers = dict(request.headers)
    headers["Authorization"] = f"Bearer {key}"
    headers.pop("host", None)

    req = client.build_request(
        method=request.method,
        url=url,
        headers=headers,
        content=body,
        params=request.query_params,
    )
    
    resp = await client.send(req, stream=True)
    
    if resp.status_code in (401, 429) and pool:
        await pool.rotate(key)
    
    return resp

@app.get("/")
async def root():
    return {"status": "ok"}

@app.api_route("/proxy/{provider}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], dependencies=[Depends(verify_master_key)])
async def proxy_handler(provider: str, path: str, request: Request):
    return await proxy_request(provider, path, request)

@app.api_route("/proxy/all/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], dependencies=[Depends(verify_master_key)])
async def universal_proxy_handler(path: str, request: Request):
    body = await request.body()
    for provider in PROVIDER_CONFIG:
        pool = get_pool(provider)
        for key in pool.keys:
            try:
                resp = await perform_request(provider, key, path, request, body, pool)
                if resp.status_code == 200:
                    return StreamingResponse(
                        resp.aiter_raw(),
                        status_code=resp.status_code,
                        headers=dict(resp.headers)
                    )
                if resp.status_code in (401, 429):
                    continue
                if resp.status_code in (400, 404):
                    break
            except Exception:
                continue
    raise HTTPException(status_code=503, detail="All providers exhausted")
