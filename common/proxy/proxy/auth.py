from .config import Settings


def build_microvm_headers(settings: Settings) -> dict[str, str]:
    return {
        "X-aws-proxy-auth": settings.token,
        "X-aws-proxy-port": settings.target_port,
    }
