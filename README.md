# User Profile Cleaner

A Windows GUI tool for IT administrators to bulk-delete stale user profiles from school/lab computers. Requires administrator privileges.

## Features

- Lists all protected (preserved) user accounts in a GUI
- Add or remove users from the protected list at runtime
- Scans the Windows registry (`ProfileList`) and `C:\Users` to find removable profiles
- Deletes profile folders and registry entries for non-protected users
- Optionally logs off the current session after cleanup

## Requirements

- Windows 10 / 11
- Python 3.x (to run from source)
- Must be run as **Administrator**

## Run from source

```bash
pip install pyinstaller   # only needed to build the exe
python UserProfileCleaner.py
```

## Build standalone executable

```bash
pyinstaller UserProfileCleaner.spec
```

The compiled binary will be in `dist/UserProfileCleaner.exe`.

## Configuration

Edit the `core_users` list near the top of `UserProfileCleaner.py` to match the IT/admin accounts that should **never** be deleted. These accounts are permanently locked and cannot be removed through the UI.

```python
core_users = [
    "Administrator",
    "Default",
    "Public",
    # add your IT accounts here
]
```

## Usage

1. Run the executable (or script) as Administrator.
2. The list shows all currently protected users.
3. Use **Add User** / **Remove User** to adjust the list for this session.
4. Click **RUN CLEANUP** — you will be prompted for confirmation before any deletions occur.
5. Optionally log off when prompted after cleanup completes.
<img width="421" height="449" alt="image" src="https://github.com/user-attachments/assets/4c0d70ca-a4eb-4d18-bd13-deb888c78cb1" />
<img width="418" height="445" alt="image" src="https://github.com/user-attachments/assets/39c05a2b-a252-4e97-97e7-b3fb6eb127e2" />

> **Warning:** This tool permanently deletes user profile folders and registry entries. Always verify the protected list before running cleanup.

## License

MIT
