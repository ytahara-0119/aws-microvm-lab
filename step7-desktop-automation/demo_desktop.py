import json
import os
import re
import time
import subprocess
from pathlib import Path


ARTIFACT_DIR = Path("/root/artifacts")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

def wait_for_windows(max_retry: int = 60, interval_sec: int = 2) -> list[dict]:
    for _ in range(max_retry):
        windows = get_windows()
        if windows:
            return windows
        time.sleep(interval_sec)
    return []


def run(command: list[str]) -> str:
    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return result.stdout


def get_resolution() -> str:
    output = run(["xrandr"])
    match = re.search(r"current\s+(\d+\s+x\s+\d+)", output)
    if match:
        return match.group(1).replace(" ", "")
    return "unknown"


def get_clients() -> list[str]:
    output = run(["xlsclients"])
    return [line.strip() for line in output.splitlines() if line.strip()]


def get_windows() -> list[dict]:
    output = run(["xwininfo", "-root", "-tree"])
    windows = []

    pattern = re.compile(
        r'^\s*(0x[0-9a-fA-F]+)\s+"([^"]*)".*?(\d+)x(\d+)\+(-?\d+)\+(-?\d+)'
    )

    for line in output.splitlines():
        match = pattern.search(line)
        if not match:
            continue

        window_id, title, width, height, x, y = match.groups()

        width = int(width)
        height = int(height)
        x = int(x)
        y = int(y)

        # Firefoxの補助ウィンドウや1x1/10x10/200x200程度の小さいWindowを除外
        if width < 300 or height < 200:
            continue

        # タイトルなしは除外
        if not title.strip():
            continue

        windows.append(
            {
                "id": window_id,
                "title": title,
                "width": width,
                "height": height,
                "x": x,
                "y": y,
            }
        )

    return windows

def take_screenshot() -> str:
    path = ARTIFACT_DIR / "desktop.png"
    run(["import", "-window", "root", str(path)])
    return str(path)



def main() -> None:
    display = os.environ.get("DISPLAY", "")

    windows = wait_for_windows(max_retry=60, interval_sec=2)
    time.sleep(5)
    screenshot = take_screenshot()

    state = {
        "display": display,
        "resolution": get_resolution(),
        "clients": get_clients(),
        "windows": windows,
        "screenshot": take_screenshot(),
    }

    output_path = ARTIFACT_DIR / "desktop-state.json"
    output_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(state, ensure_ascii=False, indent=2))
    print(f"Saved state: {output_path}")

if __name__ == "__main__":
    main()
