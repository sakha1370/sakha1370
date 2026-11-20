import base64
import json
import os
import urllib.request
from pathlib import Path

API_KEY = os.environ["WAKATIME_API_KEY"].strip()
BADGES_DIR = Path("badges")
BADGES_DIR.mkdir(exist_ok=True)


def fetch_rank(country_code: str | None = None) -> int | None:
    url = "https://wakatime.com/api/v1/leaders"
    if country_code:
        url += f"?country_code={country_code}"

    token = base64.b64encode(f"{API_KEY}:".encode()).decode()
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Basic {token}",
            "User-Agent": "sakha1370-wakatime-rank-badge",
        },
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    return (data.get("current_user") or {}).get("rank")


def pick_color(rank: int | None, is_local: bool = False) -> str:
    if rank is None:
        return "lightgrey"
    if rank <= (5 if is_local else 100):
        return "brightgreen"
    if rank <= (20 if is_local else 500):
        return "blue"
    return "orange"


def write_badge(filename: str, label: str, rank: int | None, is_local: bool = False) -> None:
    payload = {
        "schemaVersion": 1,
        "label": label,
        "message": f"#{rank}" if rank else "Unranked",
        "color": pick_color(rank, is_local=is_local),
        "namedLogo": "wakatime",
    }
    (BADGES_DIR / filename).write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    iran_rank = fetch_rank("IR")
    global_rank = fetch_rank()

    write_badge("wakatime-iran.json", "WakaTime Iran", iran_rank, is_local=True)
    write_badge("wakatime-global.json", "WakaTime Global", global_rank, is_local=False)

    print(f"Updated -> Iran: #{iran_rank}, Global: #{global_rank}")


if __name__ == "__main__":
    main()
