from fastapi import APIRouter, Request, Depends, Response
from fastapi.responses import JSONResponse
from typing import Optional

import httpx
import re

from .config import cfg, backends, routes
from .errors import HTTPabort


router = APIRouter()


@router.get('/version')
async def version():
    return {'content': f'Current version - {cfg.VERSION}'}


async def find_route(route_name, method, path, query_strings):
    try:
        route = routes[route_name]
    except Exception as e:
        HTTPabort(404, 'Route not found')
    if str(method) not in route['allowed_methods']:
        HTTPabort(422, 'Method not allowed')
    if route['route_type'] == 'static':
        if path != route['route_path']:
            HTTPabort(409, "Header and Path didn't match")
    elif route['route_type'] == 'dynamic':
        if not re.match(route['route_path'], path):
            HTTPabort(409, "Header and Path didn't match")

    destination = backends[route['destination']]
    route['link'] = f"{destination['protocol']}://{destination['host']}:{destination['port']}{path}"
    if query_strings:
        route['link'] += f'?{query_strings}'

    return route


async def get_auth_headers(token):
    async with httpx.AsyncClient() as ac:
        answer = await ac.post(cfg.AUTH_URL, json={'token': token})
        if answer.status_code == 200:
            return answer.json()['content']
        else:
            return {}


async def proxy(request, route, auth_headers=None):
    headers = dict(request.headers)
    if auth_headers:
        headers.update(auth_headers)
    async with httpx.AsyncClient() as ac:
        answer = await ac.request(request.method, route['link'], data=await request.body(), headers=headers)
        resp = Response(content=answer.content, headers=answer.headers, status_code=answer.status_code)
        return resp


@router.api_route('/{full_path:path}', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
async def path(full_path: str, request: Request, response: Response):
    try:
        route_name = request.headers[cfg.ROUTE_HEADER_NAME]
    except Exception as e:
        HTTPabort(404, 'Routing Header not found')

    route = await find_route(route_name, request.method, request.url.path, request.query_params)

    auth_headers = {}
    if route['auth_required'] or route['auth_forbidden']:
        auth_headers = await get_auth_headers(request.cookies.get(cfg.TOKEN_NAME))
        if route['auth_required'] and not auth_headers:
            HTTPabort(401, 'Unauthorized')

    if route['auth_forbidden'] and auth_headers:
        HTTPabort(409, 'User must be unauthorized')

    return await proxy(request, route, auth_headers)
