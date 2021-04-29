import logging

from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Mount, Route

from bitsapp.service import bit_service

logger = logging.getLogger(__name__)

bits_url_prefix = '/bits'
categories_url_prefix = '/categories'


async def list_bits(req):
    logger.info("getting bits")
    return JSONResponse(content=bit_service.list())

async def save_bit(req):
    data = await req.json()
    bit = bit_service.save(**data)
    return JSONResponse(content=bit)

async def new_bit(req):
    bit = bit_service.new(user={'name': 'user'})
    return JSONResponse(content=bit)


def bit_routes():
    return Mount('/api', routes=[
        Route(f'{bits_url_prefix}/new', endpoint=new_bit, methods=['GET']),
        Route(bits_url_prefix, endpoint=list_bits, methods=['GET']),
        Route(bits_url_prefix, endpoint=save_bit, methods=['POST', 'PUT']),
    ])
