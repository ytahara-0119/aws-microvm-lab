from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    endpoint: str
    token: str
    target_port: str
    listen_host: str
    listen_port: int


def load_settings() -> Settings:
    endpoint = os.environ.get("ENDPOINT")
    token = os.environ.get("TOKEN")

    if not endpoint:
        raise RuntimeError("ENDPOINT is required")

    if not token:
        raise RuntimeError("TOKEN is required")

    return Settings(
        endpoint=endpoint,
        token=token,
        target_port=os.environ.get("TARGET_PORT", "7681"),
        listen_host=os.environ.get("LISTEN_HOST", "127.0.0.1"),
        listen_port=int(os.environ.get("LISTEN_PORT", "8080")),
    )
