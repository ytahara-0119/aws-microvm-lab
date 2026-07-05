from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Route:
    prefix: str
    target_port: str
    strip_prefix: bool = True


@dataclass(frozen=True)
class Settings:
    endpoint: str
    token: str
    target_port: str
    listen_host: str
    listen_port: int
    routes: tuple[Route, ...]


def load_settings() -> Settings:
    endpoint = os.environ.get("ENDPOINT")
    token = os.environ.get("TOKEN")

    if not endpoint:
        raise RuntimeError("ENDPOINT is required")

    if not token:
        raise RuntimeError("TOKEN is required")

    target_port = os.environ.get("TARGET_PORT", "6080")

    routes = (
        Route(prefix="/terminal", target_port=os.environ.get("TERMINAL_PORT", "7681")),
        Route(prefix="/vnc", target_port=os.environ.get("VNC_PORT", "6080"), strip_prefix=False),
    )

    return Settings(
        endpoint=endpoint,
        token=token,
        target_port=target_port,
        listen_host=os.environ.get("LISTEN_HOST", "127.0.0.1"),
        listen_port=int(os.environ.get("LISTEN_PORT", "8080")),
        routes=routes,
    )
