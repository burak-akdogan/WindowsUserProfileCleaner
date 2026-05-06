import tkinter as tk
from tkinter import messagebox
import ctypes
import subprocess
import os
import winreg

# -----------------------
# ADMIN CHECK
# -----------------------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    messagebox.showerror("Admin Required", "Run as Administrator!")
    exit()

# -----------------------
# SAFE WHITELIST (DO NOT TOUCH CORE IT USERS)
# -----------------------
# Core IT users that can NEVER be removed via the UI
core_users = [
    "Administrator",
    "All Users",
    "UpdatusUser",
    "Default",
    "Default User",
    "Public"
   
]

# Working list — starts as a copy of core, extras can be added/removed
preserve_users = list(core_users)

# normalize for safety (case-insensitive compare)
def is_core(user):
    """True if user is a locked IT account that cannot be removed."""
    return user.lower() in [u.lower() for u in core_users]

def is_protected(user):
    """True if user is already in the preserve list (for add-duplicate check)."""
    return user.lower() in [u.lower() for u in preserve_users]

# -----------------------
# UI FUNCTIONS
# -----------------------
def refresh():
    listbox.delete(0, tk.END)
    for u in preserve_users:
        listbox.insert(tk.END, u)

def add_user():
    u = entry.get().strip()
    if not u:
        return

    if is_protected(u):
        messagebox.showwarning("Blocked", "This user is already protected.")
        return

    preserve_users.append(u)
    refresh()
    entry.delete(0, tk.END)

def remove_user():
    sel = listbox.curselection()
    if not sel:
        return

    u = listbox.get(sel)

    if is_core(u):
        messagebox.showerror("Blocked", "Cannot remove IT protected user!")
        return

    preserve_users.remove(u)
    refresh()

# -----------------------
# CLEANUP EXECUTION
# -----------------------
def delete_folder(path):
    """Try to delete a folder up to 3 times."""
    for _ in range(3):
        if not os.path.exists(path):
            break
        subprocess.call(["cmd.exe", "/c", "rmdir", "/s", "/q", path])

def run_cleanup():
    confirm = messagebox.askyesno(
        "WARNING",
        "This will DELETE all non-protected user profiles. Continue?"
    )
    if not confirm:
        return

    profile_list_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList"

    # --- Phase 1: Remove registry entries + folders for registered profiles ---
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, profile_list_path) as key:
            sids = []
            i = 0
            while True:
                try:
                    sids.append(winreg.EnumKey(key, i))
                    i += 1
                except OSError:
                    break
    except Exception as e:
        messagebox.showerror("Error", f"Cannot read registry:\n{e}")
        return

    for sid in sids:
        if "S-1-5-21" not in sid:
            continue

        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                f"{profile_list_path}\\{sid}") as k:
                profile_path, _ = winreg.QueryValueEx(k, "ProfileImagePath")
        except Exception:
            continue

        profile_path = os.path.expandvars(profile_path)
        folder_name  = os.path.basename(profile_path)
        username     = folder_name.split(".")[0]

        if is_protected(username):
            continue

        delete_folder(profile_path)

        # Delete registry key (use reg delete to handle keys with subkeys)
        subprocess.call(
            ["reg", "delete",
             f"HKLM\\{profile_list_path}\\{sid}",
             "/f"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

    # --- Phase 2: Scan C:\Users directly and delete leftover folders ---
    users_dir = r"C:\Users"
    try:
        entries = os.listdir(users_dir)
    except Exception as e:
        messagebox.showerror("Error", f"Cannot list C:\\Users:\n{e}")
        entries = []

    for entry in entries:
        username = entry.split(".")[0]
        if is_protected(username):
            continue
        full_path = os.path.join(users_dir, entry)
        if os.path.isdir(full_path):
            delete_folder(full_path)

    do_logoff = messagebox.askyesno(
        "Cleanup Complete",
        "Profile cleanup finished.\n\nLog off now?"
    )
    if do_logoff:
        subprocess.call(["shutdown.exe", "/l", "/f"])

# -----------------------
# UI
# -----------------------
root = tk.Tk()
root.title("School Profile Cleaner - Burak Akdogan")
root.geometry("420x420")

listbox = tk.Listbox(root)
listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

entry = tk.Entry(root)
entry.pack(fill=tk.X, padx=10)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Add User", command=add_user).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Remove User", command=remove_user).grid(row=0, column=1, padx=5)

tk.Button(root, text="RUN CLEANUP", bg="red", fg="white", command=run_cleanup).pack(pady=10)

refresh()
root.mainloop()