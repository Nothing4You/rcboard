import asyncio
import logging

import aiohttp
import aiohttp.web
import aiohttp_sse


logger = logging.getLogger("rcmproxy.api_server")


async def sse_client(request):
    async with aiohttp_sse.sse_response(request) as response:
        response: aiohttp_sse.EventSourceResponse

        app = request.app
        queue = asyncio.Queue()

        logger.info("client connected")

        async with app["api_server"].cache_lock:
            app["api_server"].channels.add(queue)

            for k, v in app["api_server"].cache.items():
                await queue.put((k, v))

        try:
            while not response.task.done():
                (type_, payload) = await queue.get()
                await response.send(payload, event=type_)
                queue.task_done()
        finally:
            app["api_server"].channels.remove(queue)
            logger.info("client disconnected")

    return response


class ApiServer:
    def __init__(self, host: str = None, port: int = None):
        if host is None:
            host = "localhost"
        self.host = host

        if port is None:
            port = 5080
        self.port = port

        self.channels = set()

        self.app = aiohttp.web.Application()
        self.app["api_server"] = self
        self.app.router.add_route("GET", "/sse", sse_client)

        self.app.router.add_static("/static", "static", append_version=True)

        self.runner = aiohttp.web.AppRunner(self.app)
        self.runner_is_setup = False
        self.site = None

        self.cache = {}

        self.cache_lock = asyncio.locks.Lock()

    async def setup_runner(self):
        if not self.runner_is_setup:
            await self.runner.setup()

        self.site = aiohttp.web.TCPSite(self.runner, self.host, self.port)

    async def start(self):
        await self.setup_runner()
        await self.site.start()

    async def distribute(self, data, type_: str = None):
        if type_ is None:
            type_ = "message"

        if type_ in self.cache and self.cache[type_] == data:
            return

        logger.info(f"Forwarding message of type: {type_}")
        logger.debug(f"forwarded message data: {data}")

        async with self.cache_lock:
            self.cache[type_] = data

            for queue in self.channels:
                await queue.put((type_, data))
