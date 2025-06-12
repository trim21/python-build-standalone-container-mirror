import os
import re
import httpx
import sys
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional

RELEASES_URL = "https://api.github.com/repos/astral-sh/python-build-standalone/releases"
# Example asset name: cpython-3.12.3+20240325-x86_64-unknown-linux-gnu-install_only.tar.gz
ASSET_PATTERN = re.compile(r".*-x86_64-unknown-linux-gnu.*")
DOWNLOAD_DIR = "artifact"


@dataclass
class Asset:
    name: str
    browser_download_url: str
    # Add other asset fields if needed


@dataclass
class ReleaseInfo:
    tag_name: str
    name: Optional[str]
    published_at: str
    assets: List[Asset] = field(default_factory=list)
    # Add other release fields if needed


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
        published_at=datetime.fromisoformat(latest_release_data["published_at"]),
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


def get_matching_assets():
    """
    Fetches CPython x86-64 Linux install_only release assets
    from the latest release of astral-sh/python-build-standalone.
    Returns a list of (asset_name, download_url) tuples.
    """
    print(f"Fetching releases from {RELEASES_URL}...")
    assets = []
    try:
        response = httpx.get(RELEASES_URL, timeout=30)
        response.raise_for_status()
        releases = response.json()
    except httpx.RequestException as e:
        print(f"Error fetching releases: {e}", file=sys.stderr)
        return []

    if not releases:
        print("No releases found.", file=sys.stderr)
        return []

    # Assuming the first release in the list is the latest
    latest_release = releases[0]
    tag_name = latest_release.get("tag_name", "Unknown tag")
    print(f"Processing latest release: {tag_name}")

    found_in_latest = False
    for asset in latest_release.get("assets", []):
        asset_name = asset.get("name", "")
        if ASSET_PATTERN.match(asset_name):
            download_url = asset.get("browser_download_url")
            if download_url:
                print(f"Found matching asset in latest release: {asset_name}")
                assets.append((asset_name, download_url))
                found_in_latest = True
            else:
                print(
                    f"Asset {asset_name} in latest release has no download URL.",
                    file=sys.stderr,
                )

    if not found_in_latest:
        print(
            f"No suitable x86-64 Linux asset found in the latest release ({tag_name}).",
            file=sys.stderr,
        )

    return assets


def download_file(url, dest_path):
    """Downloads a file from a URL to a destination path."""
    print(f"Downloading {url} to {dest_path}...")
    try:
        with httpx.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(dest_path, "wb") as f:
                for chunk in r.iter_bytes(chunk_size=8192):
                    f.write(chunk)
        print("Download complete.")
        return True
    except httpx.RequestException as e:
        print(f"Error downloading file: {e}", file=sys.stderr)
        return False
    except IOError as e:
        print(f"Error writing file: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    assets = get_matching_assets()

    if not assets:
        print("Could not find any suitable release assets. Exiting.", file=sys.stderr)
        sys.exit(1)

    downloaded_versions = []
    for asset_name, download_url in assets:
        dest_path = os.path.join(DOWNLOAD_DIR, asset_name)
        if download_file(download_url, dest_path):
            downloaded_versions.append(asset_name)
        else:
            print(f"Failed to download {asset_name}.", file=sys.stderr)
