#!/usr/bin/env python3
"""
Sync a local wiki folder to Google Drive.

Usage:
    python sync_drive_wiki.py
    python sync_drive_wiki.py second-brain/wiki
    python sync_drive_wiki.py --folder-id REMOTE_WIKI_FOLDER_ID
    python sync_drive_wiki.py --parent-folder-id REMOTE_PARENT_FOLDER_ID
    python sync_drive_wiki.py --delete-removed

Setup:
    1. Reuse the same service account credentials used by sync_drive_articles.py
    2. For first run, set WIKI_DRIVE_PARENT_FOLDER_ID or pass --parent-folder-id
    3. Optionally set WIKI_DRIVE_FOLDER_NAME to control the remote folder name
    4. After the first run, the resolved wiki folder ID is cached in .gdrive_cache/wiki_sync_state.json
"""

import argparse
import hashlib
import json
import mimetypes
import os
import sys
from collections import deque
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# === Configuration ===
SCRIPT_DIR = Path(__file__).parent
DEFAULT_LOCAL_WIKI_DIR = SCRIPT_DIR / "second-brain" / "wiki"
CACHE_DIR = SCRIPT_DIR / ".gdrive_cache"
WIKI_SYNC_STATE_FILE = CACHE_DIR / "wiki_sync_state.json"
CREDENTIALS_FILE_CANDIDATES = [
    SCRIPT_DIR / "credentials.json",
    SCRIPT_DIR / "second-brain" / "credentials.json",
]
FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"
SCOPES = ["https://www.googleapis.com/auth/drive"]


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
        with credentials_path.open("r", encoding="utf-8") as file_handle:
            return json.load(file_handle).get("client_email")
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


def load_sync_state() -> dict:
    """Load cached wiki sync state if available."""
    if not WIKI_SYNC_STATE_FILE.exists():
        return {}

    try:
        with WIKI_SYNC_STATE_FILE.open("r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
            return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        print(f"Warning: Could not read {WIKI_SYNC_STATE_FILE}; ignoring cached sync state.")
        return {}


def save_sync_state(state: dict) -> None:
    """Persist the resolved remote wiki folder ID for later runs."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with WIKI_SYNC_STATE_FILE.open("w", encoding="utf-8") as file_handle:
        json.dump(state, file_handle, indent=2, sort_keys=True)
        file_handle.write("\n")


def is_folder(file_info: dict) -> bool:
    """Return True when the Drive item is a folder."""
    return file_info.get("mimeType") == FOLDER_MIME_TYPE


def get_folder_metadata(folder_id: str, service) -> dict | None:
    """Fetch Drive metadata for a folder ID."""
    try:
        return (
            service.files()
            .get(
                fileId=folder_id,
                fields="id, name, mimeType, driveId, parents, trashed",
                supportsAllDrives=True,
            )
            .execute()
        )
    except HttpError as error:
        print(f"Error accessing folder {folder_id}: {error}")
        return None
    except Exception as error:
        print(f"Error accessing folder {folder_id}: {error}")
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
            "fields": "nextPageToken, files(id, name, mimeType, md5Checksum, parents)",
            "pageToken": page_token,
            "supportsAllDrives": True,
            "includeItemsFromAllDrives": True,
        }
        if drive_id:
            request_args["corpora"] = "drive"
            request_args["driveId"] = drive_id

        results = service.files().list(**request_args).execute()
        files.extend(results.get("files", []))
        page_token = results.get("nextPageToken")

        if not page_token:
            break

    return files


def find_child_folder_by_name(
    parent_folder_id: str, folder_name: str, service, drive_id: str | None = None
) -> dict | None:
    """Find a single child folder by name under the given parent."""
    matches = [
        item
        for item in list_folder_items(parent_folder_id, service, drive_id)
        if is_folder(item) and item["name"] == folder_name
    ]

    if len(matches) > 1:
        raise RuntimeError(
            f"Multiple remote folders named '{folder_name}' exist under parent {parent_folder_id}. "
            "Set WIKI_DRIVE_FOLDER_ID or pass --folder-id to disambiguate."
        )

    return matches[0] if matches else None


def create_folder(name: str, parent_folder_id: str, service) -> dict:
    """Create a Drive folder under the specified parent."""
    metadata = {
        "name": name,
        "mimeType": FOLDER_MIME_TYPE,
        "parents": [parent_folder_id],
    }
    return (
        service.files()
        .create(
            body=metadata,
            fields="id, name, mimeType, driveId, parents",
            supportsAllDrives=True,
        )
        .execute()
    )


def build_local_tree(local_root: Path) -> tuple[list[str], dict[str, Path]]:
    """Return relative folder paths and file paths below the local root."""
    relative_paths = sorted(
        local_root.rglob("*"),
        key=lambda path: (
            len(path.relative_to(local_root).parts),
            path.relative_to(local_root).as_posix().lower(),
        ),
    )

    folders: list[str] = []
    files: dict[str, Path] = {}

    for path in relative_paths:
        rel_path = path.relative_to(local_root).as_posix()
        if path.is_dir():
            folders.append(rel_path)
        elif path.is_file():
            files[rel_path] = path

    return folders, files


def build_remote_tree(root_folder_id: str, service, drive_id: str | None = None) -> tuple[dict, dict]:
    """Walk the remote folder tree and index items by relative path."""
    remote_folders: dict[str, dict] = {}
    remote_files: dict[str, dict] = {}
    queue = deque([("", root_folder_id)])

    while queue:
        parent_rel, folder_id = queue.popleft()
        children = sorted(
            list_folder_items(folder_id, service, drive_id),
            key=lambda item: (item["name"].lower(), item["id"]),
        )

        for child in children:
            child_rel = child["name"] if not parent_rel else f"{parent_rel}/{child['name']}"
            if child_rel in remote_folders or child_rel in remote_files:
                raise RuntimeError(
                    f"Duplicate remote path detected: {child_rel}. "
                    "Use unique names or set the exact remote wiki folder ID."
                )

            if is_folder(child):
                remote_folders[child_rel] = child
                queue.append((child_rel, child["id"]))
            else:
                remote_files[child_rel] = child

    return remote_folders, remote_files


def compute_md5(path: Path) -> str:
    """Compute the local file's md5 checksum."""
    digest = hashlib.md5()
    with path.open("rb") as file_handle:
        while True:
            chunk = file_handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def guess_mime_type(path: Path) -> str:
    """Guess a MIME type for upload, defaulting to binary."""
    mime_type, _ = mimetypes.guess_type(str(path))
    return mime_type or "application/octet-stream"


def upload_file(local_path: Path, parent_folder_id: str, service) -> dict:
    """Upload a new file into Drive."""
    media = MediaFileUpload(
        str(local_path),
        mimetype=guess_mime_type(local_path),
        resumable=False,
    )
    return (
        service.files()
        .create(
            body={"name": local_path.name, "parents": [parent_folder_id]},
            media_body=media,
            fields="id, name, md5Checksum, parents",
            supportsAllDrives=True,
        )
        .execute()
    )


def update_file(local_path: Path, file_id: str, service) -> dict:
    """Replace the contents of an existing Drive file."""
    media = MediaFileUpload(
        str(local_path),
        mimetype=guess_mime_type(local_path),
        resumable=False,
    )
    return (
        service.files()
        .update(
            fileId=file_id,
            media_body=media,
            fields="id, name, md5Checksum, parents",
            supportsAllDrives=True,
        )
        .execute()
    )


def delete_item(file_id: str, service) -> None:
    """Delete a Drive file or folder."""
    service.files().delete(fileId=file_id, supportsAllDrives=True).execute()


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Sync a local wiki folder to a Google Drive folder."
    )
    parser.add_argument(
        "local_dir",
        nargs="?",
        default=str(DEFAULT_LOCAL_WIKI_DIR),
        help="Local wiki directory to sync. Defaults to second-brain/wiki.",
    )
    parser.add_argument(
        "--folder-id",
        default=None,
        help="Exact remote Google Drive folder ID for the wiki root.",
    )
    parser.add_argument(
        "--parent-folder-id",
        default=None,
        help="Parent Drive folder ID used to create/find the wiki folder on first run.",
    )
    parser.add_argument(
        "--folder-name",
        default=None,
        help="Remote folder name to create/find when --folder-id is not provided.",
    )
    parser.add_argument(
        "--delete-removed",
        action="store_true",
        help="Delete remote files and folders that no longer exist locally.",
    )
    return parser.parse_args()


def resolve_remote_root(local_root: Path, args: argparse.Namespace, service) -> tuple[dict, bool]:
    """Find or create the remote root folder used for wiki sync."""
    state = load_sync_state()
    folder_name = (
        args.folder_name
        or os.environ.get("WIKI_DRIVE_FOLDER_NAME")
        or state.get("wiki_folder_name")
        or local_root.name
    )
    parent_folder_id = (
        args.parent_folder_id
        or os.environ.get("WIKI_DRIVE_PARENT_FOLDER_ID")
        or state.get("parent_folder_id")
    )

    folder_id_sources = [
        ("--folder-id", args.folder_id),
        ("WIKI_DRIVE_FOLDER_ID", os.environ.get("WIKI_DRIVE_FOLDER_ID")),
        ("cache", state.get("wiki_folder_id")),
    ]

    for source_name, folder_id in folder_id_sources:
        if not folder_id:
            continue

        folder_info = get_folder_metadata(folder_id, service)
        if folder_info and is_folder(folder_info):
            save_sync_state(
                {
                    "parent_folder_id": (folder_info.get("parents") or [parent_folder_id])[0],
                    "source_dir": str(local_root),
                    "wiki_folder_id": folder_info["id"],
                    "wiki_folder_name": folder_info["name"],
                }
            )
            return folder_info, False

        if source_name == "cache":
            print("Cached wiki folder ID is no longer valid. Falling back to parent-folder resolution.")
            break

        print(f"Error: {source_name} points to an inaccessible or non-folder Drive item: {folder_id}")
        sys.exit(1)

    if not parent_folder_id:
        print(
            "Error: No remote wiki folder is configured.\n"
            "Set WIKI_DRIVE_PARENT_FOLDER_ID for the first run, or set WIKI_DRIVE_FOLDER_ID "
            "if the remote wiki folder already exists."
        )
        sys.exit(1)

    parent_info = get_folder_metadata(parent_folder_id, service)
    if not parent_info or not is_folder(parent_info):
        print(f"Error: Parent folder {parent_folder_id} is not accessible as a Drive folder.")
        sys.exit(1)

    drive_id = parent_info.get("driveId")
    existing_folder = find_child_folder_by_name(parent_folder_id, folder_name, service, drive_id)
    root_folder = existing_folder or create_folder(folder_name, parent_folder_id, service)

    save_sync_state(
        {
            "parent_folder_id": parent_folder_id,
            "source_dir": str(local_root),
            "wiki_folder_id": root_folder["id"],
            "wiki_folder_name": root_folder["name"],
        }
    )

    return root_folder, existing_folder is None


def sync_wiki(args: argparse.Namespace) -> None:
    """Main wiki sync routine."""
    local_root = Path(args.local_dir).expanduser().resolve()
    if not local_root.exists() or not local_root.is_dir():
        print(f"Error: Local wiki folder does not exist: {local_root}")
        sys.exit(1)

    print(f"Syncing local wiki folder: {local_root}")

    try:
        service, credentials_path = get_drive_service()
    except Exception as error:
        print(f"Authentication failed: {error}")
        sys.exit(1)

    service_account_email = get_service_account_email(credentials_path)
    if service_account_email:
        print(f"Service account: {service_account_email}")

    root_folder, root_created = resolve_remote_root(local_root, args, service)
    drive_id = root_folder.get("driveId")
    location = "Shared Drive" if drive_id else "My Drive"
    print(f"Remote wiki folder: {root_folder['name']} ({root_folder['id']}) [{location}]")
    if root_created:
        print("First run: created the remote wiki folder.")

    local_folders, local_files = build_local_tree(local_root)
    remote_folders, remote_files = build_remote_tree(root_folder["id"], service, drive_id)

    remote_folder_ids = {"": root_folder["id"]}
    remote_folder_ids.update({rel_path: item["id"] for rel_path, item in remote_folders.items()})

    created_dirs = 0
    uploaded_files = 0
    updated_files = 0
    skipped_files = 0
    deleted_files = 0
    deleted_dirs = 0

    for rel_dir in local_folders:
        if rel_dir in remote_folders:
            continue

        parent_rel = Path(rel_dir).parent.as_posix()
        parent_rel = "" if parent_rel == "." else parent_rel
        parent_folder_id = remote_folder_ids[parent_rel]
        created = create_folder(Path(rel_dir).name, parent_folder_id, service)
        remote_folders[rel_dir] = created
        remote_folder_ids[rel_dir] = created["id"]
        created_dirs += 1
        print(f"[MKDIR] {rel_dir}")

    for rel_file, local_path in sorted(local_files.items(), key=lambda item: item[0].lower()):
        parent_rel = Path(rel_file).parent.as_posix()
        parent_rel = "" if parent_rel == "." else parent_rel
        parent_folder_id = remote_folder_ids[parent_rel]
        remote_file = remote_files.get(rel_file)
        local_md5 = compute_md5(local_path)

        if not remote_file:
            remote_files[rel_file] = upload_file(local_path, parent_folder_id, service)
            uploaded_files += 1
            print(f"[UPLOAD] {rel_file}")
            continue

        if remote_file.get("md5Checksum") != local_md5:
            remote_files[rel_file] = update_file(local_path, remote_file["id"], service)
            updated_files += 1
            print(f"[UPDATE] {rel_file}")
            continue

        skipped_files += 1
        print(f"[SKIP] {rel_file}")

    remote_only_files = sorted(set(remote_files) - set(local_files))
    remote_only_dirs = sorted(
        set(remote_folders) - set(local_folders),
        key=lambda item: (item.count("/"), item.lower()),
    )

    if remote_only_files or remote_only_dirs:
        if args.delete_removed:
            for rel_file in remote_only_files:
                delete_item(remote_files[rel_file]["id"], service)
                deleted_files += 1
                print(f"[DELETE] {rel_file}")

            for rel_dir in sorted(
                remote_only_dirs,
                key=lambda item: (item.count("/"), item.lower()),
                reverse=True,
            ):
                delete_item(remote_folders[rel_dir]["id"], service)
                deleted_dirs += 1
                print(f"[RMDIR] {rel_dir}")
        else:
            print("\nRemote-only items were left unchanged:")
            shown = 0
            for rel_file in remote_only_files[:20]:
                print(f"  file: {rel_file}")
                shown += 1
            for rel_dir in remote_only_dirs[:20]:
                print(f"  dir:  {rel_dir}")
                shown += 1
            remaining = len(remote_only_files) + len(remote_only_dirs) - shown
            if remaining > 0:
                print(f"  ... and {remaining} more")
            print("Run with --delete-removed to mirror local deletions in Drive.")

    print("\n=== Wiki Sync Complete ===")
    print(f"  Folders created: {created_dirs}")
    print(f"  Files uploaded:  {uploaded_files}")
    print(f"  Files updated:   {updated_files}")
    print(f"  Files skipped:   {skipped_files}")
    print(f"  Files deleted:   {deleted_files}")
    print(f"  Folders deleted: {deleted_dirs}")
    print(f"  Local files:     {len(local_files)}")


if __name__ == "__main__":
    try:
        sync_wiki(parse_args())
    except RuntimeError as error:
        print(f"Error: {error}")
        sys.exit(1)
    except HttpError as error:
        print(f"Drive API error: {error}")
        sys.exit(1)
