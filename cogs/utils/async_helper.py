import asyncio
import functools


async def run_async(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))


async def run_async_no_return(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))


async def timeout(function, *args, **kwargs):
    try:
        return await asyncio.wait_for(function(*args, **kwargs), timeout=10)
    except asyncio.TimeoutError:
        return False


async def run_async_with_timeout(func, *args, **kwargs):
    try:
        loop = asyncio.get_event_loop()
        future = await asyncio.wait_for(
            loop.run_in_executor(None, functools.partial(func, *args, **kwargs)),
            timeout=0.05
        )
        return future
    except asyncio.TimeoutError:
        return False


async def run_async_with_adjustable_timeout(func, timelimit=0.05, *args, **kwargs):
    try:
        loop = asyncio.get_event_loop()
        future = await asyncio.wait_for(
            loop.run_in_executor(None, functools.partial(func, *args, **kwargs)),
            timeout=timelimit
        )
        return future
    except asyncio.TimeoutError:
        return False
