from fastapi import APIRouter, Request, Depends, Response
from fastapi.responses import JSONResponse
from typing import Optional

import httpx
import re

from .config import cfg, backends, routes
from .errors import HTTPabort


router = APIRouter()


async def find_route(path, method):
    for route in routes:
        if 'path' in route:
            if method in route['allowed_methods'] and path == route['path']:
                return route
        elif 'regexp' in route:
            if method in route['allowed_methods'] and re.match(route['regexp'], path):
                return route
    return False


async def auth_check(token):
    async with httpx.AsyncClient() as ac:
        answer = await ac.post(cfg.AUTH_URL, json={'token': token})
        return answer.json()['content'] if answer.status_code == 200 else False


async def proxy(request, auth_headers):
    headers = dict(request.headers)
    if auth_headers:
        headers.update(auth_headers)
    async with httpx.AsyncClient() as ac:
        answer = await ac.request(request.method, request.url, data=await request.body(), headers=headers)
        resp = Response(content=answer.body, headers=headers, status_code=answer.status_code)
        if answer.cookies[cfg.TOKEN_NAME]:
            response.set_cookie(key=cfg.TOKEN_NAME, value=answer.cookies[cfg.TOKEN_NAME])
        return resp


@router.get('/api-version')
async def path():
    return {'answer': 'v0.0.1'}


@router.api_route('/{full_path:path}', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
async def path(full_path: str,
               request: Request,
               response: Response):

    route = await find_route(request.url.path,  request.method)
    if not route:
        HTTPabort(404, 'Route not found')

    auth_headers = {}
    if route['auth_required']:
        auth_headers = await auth_check(request.cookies.get(cfg.TOKEN_NAME))
        if not headers:
            HTTPabort(401, 'Unauthorized')

    return await proxy(request, auth_headers)
