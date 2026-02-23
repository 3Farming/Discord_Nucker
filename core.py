import aiohttp
import asyncio
import base64
from typing import Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

class DiscordSession:
    BASE_URL = "https://discord.com/api/v9"

    def __init__(self, token: str, is_bot: bool = False):
        self.token = token
        self.headers = {
            "Authorization": f"Bot {token}" if is_bot else token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, *args):
        await self._session.close()

    async def request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{endpoint}"
        for attempt in range(5):
            async with self._session.request(method, url, **kwargs) as resp:
                if resp.status == 429: 
                    retry_after = (await resp.json()).get('retry_after', 1)
                    log.warning(f"Limit exceeded. Retry in {retry_after}с")
                    await asyncio.sleep(retry_after)
                    continue
                if resp.status >= 400:
                    text = await resp.text()
                    log.error(f"HTTP {resp.status}: {text}")
                    return {}
                return await resp.json()
        return {}

    async def get(self, endpoint: str, params=None):
        return await self.request("GET", endpoint, params=params)

    async def post(self, endpoint: str, json=None):
        return await self.request("POST", endpoint, json=json)

    async def patch(self, endpoint: str, json=None):
        return await self.request("PATCH", endpoint, json=json)

    async def delete(self, endpoint: str):
        return await self.request("DELETE", endpoint)

    async def put(self, endpoint: str, json=None):
        return await self.request("PUT", endpoint, json=json)