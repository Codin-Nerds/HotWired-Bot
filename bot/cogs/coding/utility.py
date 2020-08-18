import aiohttp
from discord.ext.commands import BadArgument


async def paste(text: str) -> str:
    """Return an online bin of given text."""
    session = aiohttp.ClientSession()

    async with session.post("https://hasteb.in/documents", data=text) as post:
        if post.status == 200:
            response = await post.text()
            return f"https://hasteb.in/{response[8:-2]}"

        post = await session.post("https://bin.drlazor.be", data={"val": text})
        if post.status == 200:
            return post.url


def get_paste_link(link: str) -> str:
    domain = link.split("/")[2]

    if domain == "hastebin.com":
        if "/raw/" in link:
            return link

        token = link.split("/")[-1]  # Get the file paste token

        if "." in token:
            token = token[: token.rfind(".")]  # Remove the extension

        return f"https://hasteb.in/raw/{token}"
    else:
        # Get the Raw github paste content
        if "/raw" in link:
            return link
        return f"{link}/raw"


def get_raw(link: str) -> str:
    """Returns the url for raw version on a hastebin-like."""
    link = link.strip("<>/")

    authorized = (
        "https://hasteb.in",
        "https://gist.github.com",
        "https://gist.githubusercontent.com",
        "https://hastebin.com",
        "https://mystb.in"
    )

    if not any([link.startswith(url) for url in authorized]):
        raise BadArgument(message=f"Links accepted only from {', '.join(authorized)}.")

    return get_paste_link(link)
