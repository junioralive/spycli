import os
import requests
import subprocess
import sys
from packaging import version


base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
version_file_path = os.path.join(base_dir, 'spycli', '__version__.py')

from spycli.__version__ import __version__

def get_latest_release_info():
    try:
        print("[...] Checking for the latest SPYCLI version...", end="", flush=True)
        response = requests.get("https://api.github.com/repos/junioralive/spycli/releases/latest")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"\r[!] Error while checking for updates: {e}")
        sys.exit(1)

def check_for_updates():
    current_version = __version__
    release_info = get_latest_release_info()
    latest_version = release_info["tag_name"]

    if version.parse(current_version) < version.parse(latest_version):
        print(f"\r[+] Update available: v{current_version} -> v{latest_version}")
        download_url, file_name = None, None
        for asset in release_info["assets"]:
            if asset["name"].endswith(".whl"):
                download_url = asset["browser_download_url"]
                file_name = asset["name"]
                break
        if download_url and file_name:
            print("\r[...] Downloading the latest version...", end="", flush=True)
            update_package(download_url, file_name, latest_version)
        else:
            print("\r[!] No suitable update file found. Please check the release assets manually.")
    else:
        print("\r[✔] You are already using the latest version of SPYCLI.")

def update_package(url, file_name, new_version):
    try:
        response = requests.get(url)
        with open(file_name, "wb") as f:
            f.write(response.content)
        print("\r[...] Installing the latest version...", end="", flush=True)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", file_name])
        update_version_file(new_version)
        print("\r[✔] SPYCLI has been successfully updated to the latest version.")
        print("\r[!] Please restart the application to apply the updates.")
        sys.exit(0)
    except requests.RequestException as e:
        print(f"\r[!] Error while downloading the update: {e}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\r[!] Error during installation: {e}")
        sys.exit(1)

def update_version_file(new_version):
    with open(version_file_path, 'w') as version_file:
        version_file.write(f'__version__ = "{new_version}"\n')
        print("\r[✔] Version file updated.")
