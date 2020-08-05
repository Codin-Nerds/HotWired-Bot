import typing as t
import zlib
from functools import partial

import aiohttp

to_bytes = partial(bytes, encoding="utf-8")


def to_tio_string(couple: list) -> bytes:
    name, obj = couple[0], couple[1]

    if not obj:
        return b""

    elif type(obj) == list:

        content = ["V" + name, str(len(obj))] + obj
        return to_bytes("\x00".join(content) + "\x00")

    else:
        return to_bytes(f"F{name}\x00{len(to_bytes(obj))}\x00{obj}\x00")


class Tio:
    """Thanks to FrenchMasterSword For the TIO Wrapper."""
    def __init__(
        self,
        language: str,
        code: str,
        inputs: str = "",
        compiler_flags: t.Optional[list] = None,
        command_line_options: t.Optional[list] = None,
        args: t.Optional[list] = None
    ) -> None:

        self.backend = "https://tio.run/cgi-bin/run/api/"
        self.json = "https://tio.run/languages.json"

        strings = {
            "lang": [language],
            ".code.tio": code,
            ".input.tio": inputs,
            "TIO_CFLAGS": compiler_flags,
            "TIO_OPTIONS": command_line_options,
            "args": args,
        }

        self.request = zlib.compress(b"".join(map(to_tio_string, zip(strings.keys(), strings.values()))) + b"R", 9)[2:-4]

        if not compiler_flags:
            compiler_flags = []

        if not command_line_options:
            command_line_options = []

        if not args:
            args = []

    async def send(self) -> str:
        session = aiohttp.ClientSession()

        async with session.post(self.backend, data=self.request) as response:
            if response.status != 200:
                raise aiohttp.HttpProcessingError(response.status)

            data = await response.read()
            data = data.decode("utf-8")
            return data.replace(data[:16], "")  # remove token
