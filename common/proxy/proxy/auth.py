from .config import Settings


def build_microvm_headers(settings: Settings, target_port: str | None = None) -> dict[str, str]:
    return {
        "X-aws-proxy-auth": settings.token,
        "X-aws-proxy-port": target_port or settings.target_port,
    }
