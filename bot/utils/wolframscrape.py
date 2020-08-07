import os

import aiohttp

APPID = os.getenv("WOLFRAM_APPID")


async def get_wolfram_data(question: str, conversation_mode: str = "false", units: str = "metric") -> str:
    if conversation_mode.lower() == "yes" or conversation_mode.lower() == "true":
        params = {"appid": APPID, "i": question, "units": units}
        url = "http://api.wolframalpha.com/v1/conversation.jsp"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                data = (await resp.json())["result"]

        return data

    else:
        params = {"appid": APPID, "i": question, "units": units}
        url = "http://api.wolframalpha.com/v1/result"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                data = await resp.text()

        return data
