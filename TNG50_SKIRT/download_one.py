import sys
import os
from pathlib import Path
from urllib.request import Request, urlopen

sid = int(sys.argv[1])

url = (
    "https://www.tng-project.org/api/TNG50-1/"
    f"snapshots/99/subhalos/{sid}/skirt/skirt_atlas.tar.gz"
)

key = (Path.home() / ".tng_api_key").read_text().strip()

folder = Path("downloads")
folder.mkdir(exist_ok=True)

output = folder / f"TNG50_DR1_{sid}.tar.gz"
partial = folder / f"TNG50_DR1_{sid}.tar.gz.part"

if output.exists():
    print(f"Already downloaded: {output}", flush=True)
    sys.exit(0)

request = Request(url, headers={"API-Key": key})

print(f"Downloading subhalo {sid}...", flush=True)

with urlopen(request, timeout=120) as response:
    content_type = response.headers.get("Content-Type", "").lower()

    if "json" in content_type or "html" in content_type:
        raise RuntimeError(f"Unexpected response: {content_type}")

    total = 0
    last_report = 0

    with open(partial, "wb") as f:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break

            f.write(chunk)
            total += len(chunk)

            mb = total // (25 * 1024 * 1024)
            if mb > last_report:
                print(f"Downloaded {total / 1024**2:.1f} MB", flush=True)
                last_report = mb

os.replace(partial, output)
print(f"COMPLETE: {output}", flush=True)
