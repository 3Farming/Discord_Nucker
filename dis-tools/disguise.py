import aiohttp
import base64
from .core import DiscordSession
import asyncio
from PIL import Image
import io

async def disguise(token: str, name: str = None, pfp_url: str = None, is_bot: bool = False):
    async with DiscordSession(token, is_bot) as api:
        payload = {}
        if name:
            payload['username'] = name
        if pfp_url:
            async with aiohttp.ClientSession() as sess:
                async with sess.get(pfp_url) as resp:
                    if resp.status == 200:
                        img_data = await resp.read()
                        b64 = base64.b64encode(img_data).decode('utf-8')
                        payload['avatar'] = f"data:image/png;base64,{b64}"
                    else:
                        print(f"Failed to load avatar: HTTP {resp.status}")
                        return
        if payload:
            result = await api.patch("/users/@me", json=payload)
            if result:
                print(f"Camouflage applied. New name: {result.get('username')}")
            else:
                print("Masking failed.")
        else:
            print("No changes specified.")