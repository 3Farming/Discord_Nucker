from .core import DiscordSession
import asyncio

async def get_guild_channels(api: DiscordSession, guild_id: int):
    return await api.get(f"/guilds/{guild_id}/channels")

async def get_guild_roles(api: DiscordSession, guild_id: int):
    return await api.get(f"/guilds/{guild_id}/roles")

async def get_guild_members(api: DiscordSession, guild_id: int, limit: int = 1000):
    members = []
    after = 0
    while True:
        batch = await api.get(f"/guilds/{guild_id}/members", params={"limit": limit, "after": after})
        if not batch:
            break
        members.extend(batch)
        if len(batch) < limit:
            break
        after = batch[-1]['user']['id']
    return members

async def delete_channel(api: DiscordSession, channel_id: int):
    return await api.delete(f"/channels/{channel_id}")

async def delete_role(api: DiscordSession, guild_id: int, role_id: int):
    return await api.delete(f"/guilds/{guild_id}/roles/{role_id}")

async def create_channel(api: DiscordSession, guild_id: int, name: str, channel_type: int = 0):
 
    return await api.post(f"/guilds/{guild_id}/channels", json={"name": name, "type": channel_type})

async def ban_member(api: DiscordSession, guild_id: int, user_id: int, reason: str = ""):
    return await api.put(f"/guilds/{guild_id}/bans/{user_id}", json={"reason": reason})

async def send_message(api: DiscordSession, channel_id: int, content: str):
    return await api.post(f"/channels/{channel_id}/messages", json={"content": content})

async def delete_message(api: DiscordSession, channel_id: int, message_id: int):

    return await api.delete(f"/channels/{channel_id}/messages/{message_id}")

async def get_channel_messages(api: DiscordSession, channel_id: int, limit: int = 100):
 
    return await api.get(f"/channels/{channel_id}/messages", params={"limit": limit})