import json
import os
import re
import subprocess
import time
from pathlib import Path


ARTIFACT_DIR = Path("/root/artifacts")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


def run(command):
    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return result.stdout


def get_resolution():
    output = run(["xrandr"])
    match = re.search(r"current\s+(\d+\s+x\s+\d+)", output)
    if match:
        return match.group(1).replace(" ", "")
    return "unknown"


def get_clients():
    output = run(["xlsclients"])
    return [line.strip() for line in output.splitlines() if line.strip()]


def get_windows():
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

        if width < 300 or height < 200:
            continue

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


def wait_for_windows(max_retry=30, interval_sec=2):
    for _ in range(max_retry):
        windows = get_windows()
        if windows:
            return windows
        time.sleep(interval_sec)
    return []


def take_screenshot():
    path = ARTIFACT_DIR / "desktop.png"
    run(["import", "-window", "root", str(path)])
    return str(path)


def observe():
    windows = wait_for_windows()
    time.sleep(3)

    state = {
        "display": os.environ.get("DISPLAY", ""),
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

    return state


def main():
    state = observe()
    print(json.dumps(state, ensure_ascii=False, indent=2))
    print("Saved state: /root/artifacts/desktop-state.json")
    print("Saved screenshot: /root/artifacts/desktop.png")


if __name__ == "__main__":
    main()
