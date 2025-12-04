import httpx
from app.config import settings

async def send_to_n8n(payload: dict):
    async with httpx.AsyncClient(timeout=20) as client:
        await client.post(settings.N8N_WEBHOOK_URL, json=payload)
