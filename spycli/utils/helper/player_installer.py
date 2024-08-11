import subprocess
import os
import platform

def is_termux():
    return 'com.termux' in os.getenv('PREFIX', '')

def is_ish():
    try:
        with open('/proc/version') as f:
            return 'ish' in f.read().lower()
    except FileNotFoundError:
        return False

def install_player():
    system = platform.system().lower()
    
    if system == 'windows':
        url = 'https://sourceforge.net/projects/mpv-player-windows/files/64bit/mpv-x86_64-20231224-git-0d47e48.7z/download'
        downloaded_file = 'mpv.7z'
        extraction_path = 'C:/mpv'
        
        try:
            subprocess.run(['curl', '-L', '-o', downloaded_file, url], check=True)
            print("[^] Download complete.", flush=True)
        except subprocess.CalledProcessError as e:
            print(f"[!] An error occurred during download: {e}", flush=True)
            return

        if os.path.isfile(downloaded_file):
            os.makedirs(extraction_path, exist_ok=True)
            try:
                subprocess.run(['7z', 'x', downloaded_file, '-o' + extraction_path], check=True)
                print(f"[^] Extracted to {extraction_path}", flush=True)
            except subprocess.CalledProcessError as e:
                print(f"[!] An error occurred during extraction: {e}", flush=True)
                return

            try:
                os.remove(downloaded_file)
                print(f"[^] Deleted the file: {downloaded_file}", flush=True)
            except Exception as e:
                print(f"[!] An error occurred while deleting the file: {e}", flush=True)
        else:
            print("[!] Downloaded file not found.", flush=True)

    elif system == 'darwin':
        try:
            subprocess.run(['brew', 'install', 'mpv'], check=True)
            print("[^] MPV player installed via Homebrew.", flush=True)
        except subprocess.CalledProcessError as e:
            print(f"[!] An error occurred during installation: {e}", flush=True)

    elif system == 'linux':
        if is_termux():
            print("[^] For Android, you can download MPV from the Play Store: https://play.google.com/store/apps/details?id=is.xyz.mpv", flush=True)
        elif is_ish():
            print("[^] For iOS, you can download VLC from the App Store: https://apps.apple.com/us/app/vlc-for-mobile/id650377962", flush=True)
        else:
            try:
                distro = subprocess.run(['lsb_release', '-is'], capture_output=True, text=True).stdout.strip().lower()
                if distro in ['ubuntu', 'debian']:
                    subprocess.run(['sudo', 'apt-get', 'update'], check=True)
                    subprocess.run(['sudo', 'apt-get', 'install', '-y', 'mpv'], check=True)
                elif distro in ['fedora']:
                    subprocess.run(['sudo', 'dnf', 'install', '-y', 'mpv'], check=True)
                elif distro in ['arch']:
                    subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'mpv'], check=True)
                print("[^] MPV player installed.", flush=True)
            except subprocess.CalledProcessError as e:
                print(f"[!] An error occurred during installation: {e}", flush=True)
            except Exception as e:
                print(f"[!] An unexpected error occurred: {e}", flush=True)
    else:
        print("[!] Platform not supported or player not installed.", flush=True)
