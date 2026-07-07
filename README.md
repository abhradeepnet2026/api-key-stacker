# API Key Stacker Proxy

A minimal FastAPI proxy that rotates through a pool of API keys to bypass rate limits.

## Installation

Run the install script or install manually:
```bash
# Automatic
./install.sh  # Linux/Mac/Git-Bash
install.bat   # Windows CMD

# Manual
pip install -r requirements.txt
```

## Configuration

Create a `.env` file based on `.env.example`:

```env
MASTER_KEY=your-secure-master-key
PORT=8000

# Comma-separated keys for each provider
OPENROUTER_KEYS=key1,key2,key3
NVIDIA_KEYS=key1,key2
OLLAMA_KEYS=key1,key2
ZAI_KEYS=key1,key2
GOOGLE_KEYS=key1,key2
XAI_KEYS=key1,key2
```

## Usage

The proxy requires the `MASTER_KEY` in the `Authorization` header to operate.

### Example Request

```bash
curl -X POST "http://localhost:8000/proxy/openrouter/chat/completions" \
     -H "Authorization: Bearer your-secure-master-key" \
     -H "Content-Type: application/json" \
     -d '{"model": "gpt-4o", "messages": [{"role": "user", "content": "Hello!"}]}'
```

## Architecture

- **Key Rotation**: Uses a round-robin strategy (`itertools.cycle`) to distribute requests across available keys.
- **Auto-Rotation**: When the proxy receives a `401` or `429` from the provider, it marks the key for rotation (implicitly handled by the round-robin cycle on the next request).
- **Master Key**: A single key used by the client to authenticate with the proxy.
