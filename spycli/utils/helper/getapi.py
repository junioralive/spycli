from cryptography.fernet import Fernet
import requests
import base64

key = b'3sOYMy7Ybm3oJHNk71R6W8iVg3NcRin0tm6I7KKYE9k='
cipher = Fernet(key)

def fetch_api_key():
    url = "https://api.github.com/repos/junioralive/spycli-api/contents/keys/apikey.txt"

    try:
        response = requests.get(url)
        response.raise_for_status()
        file_content = response.json()['content']
        api_key = base64.b64decode(file_content).decode('utf-8').strip()
        return api_key
    except requests.exceptions.RequestException as e:
        print(f"[!] Error fetching API key: {e}")
        return None

def fetch_api():
    encrypted_url = fetch_api_key()
    if encrypted_url is None:
        return None
    
    try:
        decrypted_bytes = cipher.decrypt(encrypted_url.encode())
        decrypted_url = decrypted_bytes.decode()
        return decrypted_url
    except Exception as e:
        print(f"[!] Error during decryption: {e}")
        return None
