import asyncio
import logging

import aiohttp

from .log import logging_config

from .api_server import ApiServer


UPSTREAM_IP = "127.0.0.1"
UPSTREAM_PORT_WS = 8787
UPSTREAM_PORT_HTTP = 80

ENABLE_DUMMY = True
ENABLE_WS = False


PROXY_LISTEN_IP = "0.0.0.0"
PROXY_LISTEN_PORT = 5080


logging_config()
logger = logging.getLogger("rcmproxy.run")


async def ws_backend(cb, session: aiohttp.ClientSession = None):
    ws_logger = logging.getLogger("rcmproxy.run.ws_backend")

    if session is None:
        session = aiohttp.ClientSession()

    while True:
        try:
            async with session.ws_connect(
                f"http://{UPSTREAM_IP}:{UPSTREAM_PORT_WS}/"
            ) as ws:
                async for msg in ws:
                    msg: aiohttp.WSMessage

                    if msg.type == aiohttp.WSMsgType.TEXT:
                        ws_logger.debug("Received WSMessage of type WSMsgType.TEXT")
                        await cb(msg.data, type_="StreamingData")

                    else:
                        ws_logger.warning(f"Unexpexted WSMsgType: {msg.type}")
                        ws_logger.debug(msg)

        except aiohttp.ClientError as e:
            ws_logger.debug(e, exc_info=True)
            ws_logger.warning(e)
            await asyncio.sleep(0.1)


async def dummy_backend(cb):
    from .dummy_backend import data

    while True:
        for line in data:
            await cb(line, type_="StreamingData")
            await asyncio.sleep(0.2)


async def main():
    f = []

    timeout = aiohttp.ClientTimeout(sock_connect=5, total=30)

    cs = aiohttp.ClientSession(timeout=timeout)

    api_server = ApiServer(host=PROXY_LISTEN_IP, port=PROXY_LISTEN_PORT)
    await api_server.start()

    async def cb(data: str, type_: str = None):
        await api_server.distribute(data, type_)

    if ENABLE_WS:
        f.append(ws_backend(cb, cs))

    if ENABLE_DUMMY:
        f.append(dummy_backend(cb))

    await asyncio.gather(*f)
