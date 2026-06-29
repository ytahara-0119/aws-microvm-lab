import asyncio
from aiohttp import web, ClientSession, WSMsgType

from .auth import build_microvm_headers
from .config import Settings


async def proxy_websocket(
    request: web.Request,
    settings: Settings,
    target_url: str,
) -> web.WebSocketResponse:
    ws_browser = web.WebSocketResponse(protocols=("tty",))
    await ws_browser.prepare(request)

    headers = build_microvm_headers(settings)

    async with ClientSession() as session:
        async with session.ws_connect(
            target_url,
            headers=headers,
            protocols=("tty",),
        ) as ws_microvm:

            async def browser_to_microvm() -> None:
                async for msg in ws_browser:
                    if msg.type == WSMsgType.TEXT:
                        await ws_microvm.send_str(msg.data)
                    elif msg.type == WSMsgType.BINARY:
                        await ws_microvm.send_bytes(msg.data)
                    elif msg.type in (WSMsgType.CLOSE, WSMsgType.ERROR):
                        await ws_microvm.close()

            async def microvm_to_browser() -> None:
                async for msg in ws_microvm:
                    if msg.type == WSMsgType.TEXT:
                        await ws_browser.send_str(msg.data)
                    elif msg.type == WSMsgType.BINARY:
                        await ws_browser.send_bytes(msg.data)
                    elif msg.type in (WSMsgType.CLOSE, WSMsgType.ERROR):
                        await ws_browser.close()

            await asyncio.gather(
                browser_to_microvm(),
                microvm_to_browser(),
            )

    return ws_browser
