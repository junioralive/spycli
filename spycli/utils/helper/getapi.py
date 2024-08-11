import requests
import base64

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
    api_url = fetch_api_key()
    if api_url is None:
        return None
    
    return api_url
