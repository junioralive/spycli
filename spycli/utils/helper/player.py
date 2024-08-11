import subprocess
import os
import platform
import time
from spycli.utils.helper.player_installer import install_player

def is_termux():
    return 'com.termux' in os.getenv('PREFIX', '')

def is_ish():
    try:
        with open('/proc/version') as f:
            return 'ish' in f.read().lower()
    except FileNotFoundError:
        return False

def ply(streaming_link, media_title="SPYCLI", subtitle_link=None):
    url = streaming_link
    referrer = 'https://github.com/junioralive/spycli'
    
    if not url:
        print("[!] No streaming link provided.")
        return

    system = platform.system().lower()
    command = []

    try:
        if system == 'windows':
            mpv_path = r"C:\mpv\mpv.exe"
            if not os.path.exists(mpv_path):
                print(f"[!] MPV player not found, Please wait while we install...")
                install_player()
            
            command = [mpv_path, f"--referrer={referrer}", url, f"--force-media-title={media_title}"]
            if subtitle_link:
                command.append(f"--sub-file={subtitle_link}")

        elif system == 'linux':
            if is_termux():
                command = ["am", "start", "-n", "is.xyz.mpv/is.xyz.mpv.MPVActivity", "-e", "filepath", url]
                if subtitle_link:
                    command.extend(["--es", "subtitles", subtitle_link])
            elif is_ish():
                print(f"\033]8;;vlc://{url}\033\\-------------------------\n- Tap to open -\n-------------------------\033]8;;\033\\\n")
                input("[^] Press Enter to continue...")
                return
            else:
                try:
                    distro = subprocess.run(['lsb_release', '-is'], capture_output=True, text=True).stdout.strip().lower()
                    if distro in ['ubuntu', 'debian', 'fedora', 'arch']:
                        command = ["mpv", f"--referrer={referrer}", url, f"--force-media-title={media_title}"]
                        if subtitle_link:
                            command.append(f"--sub-file={subtitle_link}")
                    else:
                        print("[!] Unsupported Linux distribution.")
                        return
                except subprocess.CalledProcessError as e:
                    print(f"[!] Error determining Linux distribution: {e}")
                    return
                except Exception as e:
                    print(f"[!] Unexpected error: {e}")
                    return

        elif system == 'darwin':
            command = ["mpv", f"--referrer={referrer}", url, f"--force-media-title={media_title}"]
            if subtitle_link:
                command.append(f"--sub-file={subtitle_link}")

        if command:
            subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("[^] Playing, please wait...")
            time.sleep(2)
        else:
            try:
                install_player()
                subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("[^] Playing, please wait...")
                time.sleep(2)
            except Exception as e:
                print("[!] Platform not supported or player not installed.")
                print(f"[!] Error: {e}")
                exit(1)

    except subprocess.CalledProcessError as e:
        print(f"[!] Subprocess error: {e}")
    except FileNotFoundError as e:
        print(f"[!] File not found error: {e}")
    except Exception as e:
        print(f"[!] An unexpected error occurred: {e}")
  