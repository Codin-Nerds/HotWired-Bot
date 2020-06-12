"""
Reducing code complexity (sorta) by wrapping aiohttp GET
into a simple function.
"""
from cogs.common import user_agent
from aiohttp import ClientSession


async def get_req(session: ClientSession, url: str):
    return await session.get(url, headers=user_agent)
