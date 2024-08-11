import requests
from spycli.utils.helper.getapi import fetch_api

class TMDBClient:
    def __init__(self):
        self.base_api_url = fetch_api()
        if not self.base_api_url:
            print("[!] Something went wrong with API, please contact the developer.")
            exit(1)
    
    def fetch_api(self, endpoint, params=None):
        url = f"{self.base_api_url}{endpoint}"
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print("[!] Error: Received non-200 status code from API.")
                return None
        except requests.exceptions.ConnectionError:
            print("[!] An error occurred: Failed to establish a new connection with the API.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[!] An error occurred: {e}")
            return None
        except Exception as e:
            print(f"[!] An unexpected error occurred: {e}")
            return None

    def search(self, query):
        return self.fetch_api(f"tmdb/search?query={query}")

    def get_details(self, url):
        tmdb_id = url.split('/tv/')[-1] 
        return self.fetch_api(f"tmdb/fetch?id={tmdb_id}")
