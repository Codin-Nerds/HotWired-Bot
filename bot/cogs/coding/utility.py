import aiohttp
from discord.ext.commands import BadArgument


def get_raw(link: str) -> str:
    """Returns the url for raw version on a hastebin-like."""
    link = link.strip("<>/")  # Allow for no-embed links

    authorized = (
        "https://hasteb.in",
        "https://gist.github.com",
        "https://gist.githubusercontent.com",
    )

    if not any([link.startswith(url) for url in authorized]):
        raise BadArgument(message=f"Links accepted only from {', '.join(authorized)}.")

    domain = link.split("/")[2]

    if domain == "hasteb.in":
        if "/raw/" in link:
            return link
        token = link.split("/")[-1]
        if "." in token:
            token = token[: token.rfind(".")]  # removes extension
        return f"https://hasteb.in/raw/{token}"
    else:
        # Github uses redirection so raw -> usercontent and no raw -> normal
        # We still need to ensure we get a raw version after this potential redirection
        if "/raw" in link:
            return link
        return link + "/raw"


async def paste(text: str) -> str:
    """Return an online bin of given text."""
    async with aiohttp.ClientSession() as aioclient:
        post = await aioclient.post("https://hasteb.in/documents", data=text)
        if post.status == 200:
            response = await post.text()
            return f"https://hasteb.in/{response[8:-2]}"

        # Fallback bin
        post = await aioclient.post("https://bin.drlazor.be", data={"val": text})
        if post.status == 200:
            return post.url
