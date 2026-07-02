import asyncio
from aiohttp import web, ClientSession, WSMsgType

from .auth import build_microvm_headers
from .config import Settings


def get_websocket_protocols(request: web.Request) -> tuple[str, ...]:
    value = request.headers.get("Sec-WebSocket-Protocol", "")
    if not value:
        return ()
    return tuple(
        item.strip()
        for item in value.split(",")
        if item.strip()
    )


async def proxy_websocket(
    request: web.Request,
    settings: Settings,
    target_url: str,
) -> web.WebSocketResponse:
    protocols = get_websocket_protocols(request)

    ws_browser = web.WebSocketResponse(protocols=protocols)
    await ws_browser.prepare(request)

    headers = build_microvm_headers(settings)

    async with ClientSession() as session:
        async with session.ws_connect(
            target_url,
            headers=headers,
            protocols=protocols,
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
