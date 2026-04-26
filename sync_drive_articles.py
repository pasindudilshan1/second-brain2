#!/usr/bin/env python3
"""
Sync markdown files from a Google Drive folder to raw/articles/

Usage:
    python sync_drive_articles.py
    python sync_drive_articles.py --limit 5

Setup:
    1. Create a service account in Google Cloud Console
    2. Download the JSON key file
    3. Share your Drive folder with the service account email
    4. Set GOOGLE_APPLICATION_CREDENTIALS env var to the key file path
    5. Set DRIVE_FOLDER_ID in this script or as env var
"""

import argparse
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# === Configuration ===
SCRIPT_DIR = Path(__file__).parent
ARTICLES_DIR = SCRIPT_DIR / "second-brain" / "raw" / "articles"
TOKEN_DIR = SCRIPT_DIR / ".gdrive_cache"
CREDENTIALS_FILE_CANDIDATES = [
    SCRIPT_DIR / "credentials.json",
    SCRIPT_DIR / "second-brain" / "credentials.json",
]

# Replace with your Drive folder ID (from the URL: drive.google.com/drive/folders/THIS_ID)
DRIVE_FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID", "1dXnz9rnFSDNlUpdwcFO1a_EabKP2P8et")

# Service account scopes
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# === Helper Functions ===


def resolve_credentials_file() -> Path | None:
    """Find the service account JSON key file."""
    env_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if env_path:
        return Path(env_path)

    for candidate in CREDENTIALS_FILE_CANDIDATES:
        if candidate.exists():
            return candidate

    return None


def get_service_account_email(credentials_path: Path | None) -> str | None:
    """Extract the service account email for troubleshooting output."""
    if not credentials_path or not credentials_path.exists():
        return None

    try:
        with credentials_path.open("r", encoding="utf-8") as f:
            return json.load(f).get("client_email")
    except (OSError, json.JSONDecodeError):
        return None


def get_drive_service():
    """Authenticate and return a Drive API service client."""
    credentials_path = resolve_credentials_file()

    if not credentials_path or not credentials_path.exists():
        searched_paths = "\n".join(f"  {path}" for path in CREDENTIALS_FILE_CANDIDATES)
        print(
            "Error: No credentials found.\n"
            "Set GOOGLE_APPLICATION_CREDENTIALS env var or place service account key at:\n"
            f"{searched_paths}"
        )
        sys.exit(1)

    creds = service_account.Credentials.from_service_account_file(
        str(credentials_path), scopes=SCOPES
    )
    service = build("drive", "v3", credentials=creds)
    return service, credentials_path


def get_folder_metadata(folder_id: str, service) -> dict | None:
    """Fetch folder metadata so empty results can be diagnosed correctly."""
    try:
        return (
            service.files()
            .get(
                fileId=folder_id,
                fields="id, name, mimeType, driveId, trashed",
                supportsAllDrives=True,
            )
            .execute()
        )
    except HttpError as e:
        print(f"Error accessing folder {folder_id}: {e}")
        return None
    except Exception as e:
        print(f"Error accessing folder {folder_id}: {e}")
        return None


def list_folder_items(folder_id: str, service, drive_id: str | None = None) -> list[dict]:
    """List direct children in the specified Drive folder."""
    files = []
    page_token = None

    query = f"'{folder_id}' in parents and trashed = false"

    while True:
        request_args = {
            "q": query,
            "pageSize": 100,
            "fields": "nextPageToken, files(id, name, modifiedTime, size, md5Checksum, mimeType)",
            "pageToken": page_token,
            "supportsAllDrives": True,
            "includeItemsFromAllDrives": True,
        }
        if drive_id:
            request_args["corpora"] = "drive"
            request_args["driveId"] = drive_id

        try:
            results = service.files().list(**request_args).execute()
        except HttpError as e:
            print(f"Error listing files: {e}")
            return []
        except Exception as e:
            print(f"Error listing files: {e}")
            return []

        files.extend(results.get("files", []))
        page_token = results.get("nextPageToken")

        if not page_token:
            break

    # Debug: show what was found
    if files:
        print(f"Debug: Found {len(files)} item(s):")
        for f in files[:5]:
            print(f"  - {f['name']} ({f.get('mimeType', 'unknown')})")
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more")

    return files


def is_markdown_file(file_info: dict) -> bool:
    """Accept plain markdown files only."""
    name = file_info["name"].lower()
    mime_type = file_info.get("mimeType", "")
    return name.endswith((".md", ".markdown")) or mime_type == "text/markdown"


def parse_remote_mtime(file_info: dict) -> datetime:
    """Parse a Drive modifiedTime string into an aware datetime."""
    return datetime.fromisoformat(file_info["modifiedTime"].replace("Z", "+00:00"))


def get_local_files() -> dict[str, dict]:
    """Get existing .md files in articles folder with their metadata."""
    local_files = {}

    if not ARTICLES_DIR.exists():
        ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
        return local_files

    for pattern in ("*.md", "*.markdown"):
        for f in ARTICLES_DIR.glob(pattern):
            stat = f.stat()
            local_files[f.name] = {
                "path": f,
                "size": stat.st_size,
                "mtime": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
            }

    return local_files


def download_file(file_id: str, file_name: str, service) -> Path | None:
    """Download a file from Drive to the articles folder."""
    dest_path = ARTICLES_DIR / file_name

    try:
        request = service.files().get_media(fileId=file_id)

        with open(dest_path, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    print(f"  Downloading {file_name}: {int(status.progress() * 100)}%")

        return dest_path

    except HttpError as e:
        print(f"  Error downloading {file_name}: {e}")
        return None
    except Exception as e:
        print(f"  Error downloading {file_name}: {e}")
        return None


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Sync markdown files from a Google Drive folder to second-brain/raw/articles/."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Sync at most this many newest new or updated markdown files from Drive.",
    )
    args = parser.parse_args()

    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be greater than 0")

    return args


def classify_remote_files(
    remote_files: list[dict], local_files: dict[str, dict]
) -> tuple[list[dict], list[dict]]:
    """Split remote markdown files into download targets and up-to-date items."""
    download_targets = []
    up_to_date = []

    for remote in remote_files:
        file_name = remote["name"]
        remote_mtime = parse_remote_mtime(remote)
        local = local_files.get(file_name)

        if not local:
            download_targets.append(
                {
                    "action": "NEW",
                    "remote": remote,
                    "remote_mtime": remote_mtime,
                    "local_mtime": None,
                }
            )
            continue

        local_mtime = local["mtime"]
        if remote_mtime > local_mtime:
            download_targets.append(
                {
                    "action": "UPDATE",
                    "remote": remote,
                    "remote_mtime": remote_mtime,
                    "local_mtime": local_mtime,
                }
            )
        else:
            up_to_date.append(
                {
                    "action": "SKIP",
                    "remote": remote,
                    "remote_mtime": remote_mtime,
                    "local_mtime": local_mtime,
                }
            )

    download_targets.sort(
        key=lambda item: (item["remote_mtime"], item["remote"]["name"].lower()),
        reverse=True,
    )
    up_to_date.sort(key=lambda item: item["remote"]["name"].lower())

    return download_targets, up_to_date


def sync_files(limit: int | None = None):
    """Main sync logic - pull new/updated .md files from Drive."""

    print(f"Syncing markdown files from Drive folder: {DRIVE_FOLDER_ID}")
    print(f"Destination: {ARTICLES_DIR}\n")

    # Ensure destination exists
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

    # Connect to Drive
    try:
        service, credentials_path = get_drive_service()
    except Exception as e:
        print(f"Authentication failed: {e}")
        sys.exit(1)

    service_account_email = get_service_account_email(credentials_path)

    print("Checking Drive folder access...")
    folder_info = get_folder_metadata(DRIVE_FOLDER_ID, service)
    if not folder_info:
        if service_account_email:
            print(f"Service account: {service_account_email}")
        print("\nTroubleshooting:")
        print("  1. Check that the folder ID is correct")
        print("  2. Ensure the service account can access that exact folder")
        print("  3. If the folder is in a Shared Drive, add the service account to the Shared Drive")
        return

    if folder_info.get("mimeType") != "application/vnd.google-apps.folder":
        print(f"Error: {DRIVE_FOLDER_ID} is not a folder. Mime type: {folder_info.get('mimeType')}")
        return

    location = "Shared Drive" if folder_info.get("driveId") else "My Drive"
    print(f"Connected to folder: {folder_info['name']} ({location})\n")

    # Get remote files
    print("Scanning Drive folder...")
    remote_items = list_folder_items(DRIVE_FOLDER_ID, service, folder_info.get("driveId"))
    remote_files = [item for item in remote_items if is_markdown_file(item)]

    if not remote_items:
        print("No items found in Drive folder.")
        print("\nTroubleshooting:")
        print("  1. Check that the folder ID is correct")
        if service_account_email:
            print(f"  2. Ensure {service_account_email} has access to the folder")
        else:
            print("  2. Ensure the service account has access to the folder")
        if folder_info.get("driveId"):
            print("  3. If this is a Shared Drive, add the service account as a Shared Drive member")
        else:
            print("  3. Verify the folder is not empty")
        print("  4. This script scans direct children only; nested folders are not traversed")
        return

    if not remote_files:
        print("No markdown files found in Drive folder.")
        print("\nFound these non-markdown items:")
        for item in remote_items[:10]:
            print(f"  - {item['name']} ({item.get('mimeType', 'unknown')})")
        if len(remote_items) > 10:
            print(f"  ... and {len(remote_items) - 10} more")
        print("\nNote: this script only downloads direct child `.md` or `.markdown` files.")
        return

    print(f"Found {len(remote_files)} markdown file(s) in Drive\n")

    # Get local files
    local_files = get_local_files()

    download_targets, up_to_date = classify_remote_files(remote_files, local_files)
    deferred_targets = []

    if limit is not None:
        print(f"Applying sync limit: newest {limit} new or updated markdown file(s)\n")
        deferred_targets = download_targets[limit:]
        download_targets = download_targets[:limit]

    # Sync logic
    new_count = 0
    updated_count = 0
    skipped_count = len(up_to_date)
    deferred_count = len(deferred_targets)

    for target in download_targets:
        remote = target["remote"]
        file_name = remote["name"]
        file_id = remote["id"]

        if target["action"] == "NEW":
            print(f"[NEW] {file_name}")
            if download_file(file_id, file_name, service):
                new_count += 1
            continue

        print(
            f"[UPDATE] {file_name} "
            f"(remote: {target['remote_mtime']}, local: {target['local_mtime']})"
        )
        if download_file(file_id, file_name, service):
            updated_count += 1

    for item in up_to_date:
        print(f"[SKIP] {item['remote']['name']} (up to date)")

    if deferred_targets:
        print("\nDeferred by limit:")
        for target in deferred_targets:
            print(f"  - {target['remote']['name']} ({target['action'].lower()})")

    # Summary
    print(f"\n=== Sync Complete ===")
    print(f"  New files:       {new_count}")
    print(f"  Updated files:   {updated_count}")
    print(f"  Skipped:         {skipped_count}")
    print(f"  Deferred:        {deferred_count}")
    print(f"  Sync candidates: {len(download_targets) + deferred_count}")
    print(f"  Total in Drive:  {len(remote_files)}")


if __name__ == "__main__":
    args = parse_args()
    sync_files(limit=args.limit)
