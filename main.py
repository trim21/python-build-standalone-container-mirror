import os
from pathlib import Path
import re
import httpx
import sys
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Optional

import tqdm

RELEASES_URL = "https://api.github.com/repos/astral-sh/python-build-standalone/releases"
# Example asset name: cpython-3.12.3+20240325-x86_64-unknown-linux-gnu-install_only.tar.gz
ASSET_PATTERN = re.compile(r".*-x86_64-unknown-linux-gnu.*")
DOWNLOAD_DIR = "artifact"


@dataclass(frozen=True, slots=True)
class Asset:
    name: str
    browser_download_url: str
    # Add other asset fields if needed


@dataclass(frozen=True, slots=True)
class ReleaseInfo:
    tag_name: str
    name: Optional[str]
    published_at: datetime
    assets: List[Asset]


def get_latest_release_info():
    """
    Fetches the latest release information from astral-sh/python-build-standalone
    using the dedicated 'latest' release endpoint.
    Returns a ReleaseInfo dataclass instance or raises an exception if an error occurs.
    """

    latest_release_api_url = RELEASES_URL + "/latest"

    print(f"Fetching latest release information from {latest_release_api_url}...")
    response = httpx.get(latest_release_api_url, timeout=30)
    response.raise_for_status()  # Raises HTTPStatusError for 4xx/5xx responses
    latest_release_data = response.json()

    release_info = ReleaseInfo(
        tag_name=latest_release_data["tag_name"],
        name=latest_release_data["name"],
        published_at=datetime.fromisoformat(
            latest_release_data["published_at"]
        ).astimezone(),
        assets=[
            Asset(
                name=asset_data["name"],
                browser_download_url=asset_data["browser_download_url"],
            )
            for asset_data in latest_release_data["assets"]
        ],
    )

    print(f"Successfully fetched latest release: {release_info.tag_name}")
    return release_info


def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    release = get_latest_release_info()

    now = datetime.now().astimezone()
    if now - release.published_at <= timedelta(hours=24):
        print("latest release in 1 day, skip")
        return

    client = httpx.Client()

    for asset in tqdm.tqdm(
        [a for a in release.assets if ASSET_PATTERN.match(a.name)], ascii=True
    ):
        dest_path = Path(DOWNLOAD_DIR, asset.name)
        content = (
            client.get(asset.browser_download_url, follow_redirects=True)
            .raise_for_status()
            .content
        )

        dest_path.write_bytes(content)

    with open("version.txt", "w") as f:
        f.write(release.tag_name)


if __name__ == "__main__":
    main()
