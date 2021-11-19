import os
import asyncio
import yaml

from datetime import datetime, timezone, timedelta
from aiofiles import open as async_open
from aiofiles.os import stat as async_stat
from types import SimpleNamespace


class YamlConfigManager:
    def __init__(self, interval):
        self._update_interval = interval
        self._config_file = 'config.yaml'
        self._routes_file = 'routes2.yaml'

    async def _update_loop(self, config, backends, routes):
        while True:
            try:
                await self._update(config, backends, routes)
            except Exception as e:
                print(f'Failed to update config, see you next time \n{repr(e)}')
            await asyncio.sleep(self._update_interval)

    async def _update(self, config, backends, routes):
        config_stat = await async_stat(self._config_file)
        routes_stat = await async_stat(self._routes_file)

        mod_config_datetime = datetime.fromtimestamp(config_stat.st_mtime)
        mod_routes_datetime = datetime.fromtimestamp(routes_stat.st_mtime)

        if not config.FIRST_RUN and datetime.now() > mod_config_datetime + timedelta(seconds=self._update_interval):
            pass
        else:
            async with async_open(self._config_file, mode='r') as conf:
                data = yaml.safe_load(await conf.read())

                config.VERSION = data['version']

                config.DOMAIN = data['domain']
                self._update_interval = data['update_interval']

                config.TOKEN_NAME = data['token_name']
                config.ROUTE_HEADER_NAME = data['route_header_name']

                backends.clear()
                backends.update(data['backends'])

                for key in backends:
                    if key.find('auth'):
                        srv = backends[key]
                        config.AUTH_URL = f"http://{srv['host']}:{srv['port']}{srv['route']}"
                        break

        if not config.FIRST_RUN and datetime.now() > mod_routes_datetime + timedelta(seconds=self._update_interval):
            pass
        else:
            async with async_open(self._routes_file, mode='r') as rconf:
                routes.clear()
                routes.update(yaml.safe_load(await rconf.read()))

        cfg.FIRST_RUN = False

    async def start(self, config, backends, routes):
        await self._update(config, backends, routes)
        self._update_task = asyncio.ensure_future(self._update_loop(config, backends, routes))


cfg = SimpleNamespace()
cfg.FIRST_RUN = True

routes = {}
backends = {}
