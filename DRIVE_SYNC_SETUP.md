# Google Drive Sync Setup

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-drive-sync.txt
```

### 2. Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google Drive API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Drive API" and enable it
4. Create service account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Give it a name (e.g., "drive-sync")
   - Click "Create and Continue"
   - Skip role assignment (not needed for readonly)
   - Click "Done"
5. Create key:
   - Click on the service account email
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Select **JSON** format
   - Download the key file
6. Save the key file as `credentials.json` in this project root (preferred), OR in `second-brain/credentials.json`, OR set environment variable:
   ```bash
   set GOOGLE_APPLICATION_CREDENTIALS="C:\Users\USER\Downloads\alert-library-462616-m7-8dd045c21412.json"
   ```

### 3. Share Drive Folder

1. Open your Google Drive folder containing markdown files
2. Click "Share"
3. Add the service account email (looks like `drive-sync@project-id.iam.gserviceaccount.com`)
4. Give it **Viewer** access
5. If the folder is inside a **Shared Drive**, also add the service account as a member of that Shared Drive
6. Copy the folder ID from the URL: `drive.google.com/drive/folders/THIS_IS_THE_ID`

### 4. Configure Script

Edit `sync_drive_articles.py` and replace the default folder ID, or set:

```bash
set DRIVE_FOLDER_ID="YOUR_FOLDER_ID_HERE"
```

### 5. Run Sync

```bash
python sync_drive_articles.py
```

## How It Works

- Scans the Drive folder for `.md` files
- Validates that the folder ID is accessible before syncing
- Supports folders stored in Shared Drives
- Downloads new files to `raw/articles/`
- Updates files that have changed remotely
- Skips files that are up to date
- Preserves existing local files
- Only scans direct child files; nested folders are not traversed

## Running Again

Just run the same command - it will only pull new or updated files:

```bash
python sync_drive_articles.py
```
