from fastapi import APIRouter, Request, Depends, Response
from fastapi.responses import JSONResponse
from typing import Optional

import httpx


router = APIRouter()


async def proxy(request):
    async with httpx.AsyncClient() as ac:
        answer = await ac.request(request.method, request.url, data=await request.body(), headers=request.headers)


@router.get('/api-version')
async def path():
    return {'answer': 'custom path'}


@router.api_route('/{full_path:path}', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
async def path(full_path: str,
               request: Request,
               response: Response):

    return {'url': request.url,
            'url.path': request.url.path,
            'url.port': request.url.port,
            'url.scheme': request.url.scheme,
            'headers': request.headers,
            'methods': request.method
    }
