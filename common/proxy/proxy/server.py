from aiohttp import web, ClientSession

from .auth import build_microvm_headers
from .config import Settings, load_settings
from .websocket import proxy_websocket


def build_target_url(settings: Settings, path: str, query: str) -> str:
    url = f"https://{settings.endpoint}/{path}"
    if query:
        url += f"?{query}"
    return url


def is_websocket_request(request: web.Request) -> bool:
    return request.headers.get("Upgrade", "").lower() == "websocket"


async def handler(request: web.Request) -> web.StreamResponse:
    settings: Settings = request.app["settings"]

    path = request.match_info.get("path", "")
    target_url = build_target_url(
        settings=settings,
        path=path,
        query=request.query_string,
    )

    if is_websocket_request(request):
        return await proxy_websocket(
            request=request,
            settings=settings,
            target_url=target_url,
        )

    headers = build_microvm_headers(settings)

    async with ClientSession() as session:
        async with session.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=await request.read(),
            allow_redirects=False,
        ) as resp:
            body = await resp.read()

            response_headers = {
                key: value
                for key, value in resp.headers.items()
                if key.lower()
                not in {
                    "content-encoding",
                    "content-length",
                    "transfer-encoding",
                    "connection",
                }
            }

            return web.Response(
                body=body,
                status=resp.status,
                headers=response_headers,
            )


def create_app(settings: Settings) -> web.Application:
    app = web.Application()
    app["settings"] = settings
    app.router.add_route("*", "/", handler)
    app.router.add_route("*", "/{path:.*}", handler)
    return app


def main() -> None:
    settings = load_settings()
    app = create_app(settings)

    print(f"Proxy: http://{settings.listen_host}:{settings.listen_port}")
    print(f"Target: https://{settings.endpoint}")
    print(f"Port:   {settings.target_port}")

    web.run_app(
        app,
        host=settings.listen_host,
        port=settings.listen_port,
    )


if __name__ == "__main__":
    main()
