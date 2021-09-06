import os
import asyncio
import yaml
import re
from aiofile import async_open
from types import SimpleNamespace


class YamlConfigManager:
    def __init__(self, interval):
        self._update_interval = interval
        self._config_file = 'config.yaml'
        self._routes_file = 'routes.yaml'


    async def _update_loop(self, config, backends, routes):
        while True:
            try:
                await self._update(config, backends, routes)
            except Exception as e:
                print(f'Failed to update config, see you next time \n{repr(e)}')
            await asyncio.sleep(self._update_interval)


    async def _update(self, config, backends, routes):
        async with async_open(self._config_file, 'r') as f:
            data = yaml.safe_load(await f.read())

            config.DOMAIN = data['domain']
            self._update_interval = data['update_interval']

            config.TOKEN_NAME = data['token_name']

            backends.clear()
            backends.update(data['backends'])

            for key in backends:
                if key.find('auth'):
                    srv = backends[key]
                    config.AUTH_URL = f"http://{srv['host']}:{srv['port']}{srv['route']}"
                    break

        async with async_open(self._routes_file, 'r') as f:
            routes[:] = yaml.safe_load(await f.read())


    async def start(self, config, backends, routes):
        await self._update(config, backends, routes)
        self._update_task = asyncio.ensure_future(self._update_loop(config, backends, routes))


cfg = SimpleNamespace()

cfg.STARTUP_DB_ACTION = False

routes = []
backends = {}
