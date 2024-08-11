from spycli.utils.helper.getapi import fetch_api
import requests

class MoviesDriveAPI:
    def __init__(self):
        self.base_api_url = fetch_api()
        if not self.base_api_url:
            print("[!] Something went wrong with API, please contact the developer.")
            exit(1)

    def search(self, search_query):
        try:
            full_api_url = f'{self.base_api_url}moviesdrive/search?query={search_query}'
            response = requests.get(full_api_url)
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

    def fetch_details(self, url_id):
        try:
            full_api_url = f'{self.base_api_url}moviesdrive/detail?id={url_id}'
            response = requests.get(full_api_url)
            if response.status_code == 200:
                return response.json()
            else:
                print("[!] Error: Received non-200 status code from API.")
                return None
        except requests.exceptions.RequestException as e:
            print(f"[!] An error occurred during the request: {e}")
            return None
        except Exception as e:
            print(f"[!] An unexpected error occurred: {e}")
            return None

    def fetch_quality(self, quality_id):
        try:
            full_api_url = f'{self.base_api_url}moviesdrive/quality?id={quality_id}'
            response = requests.get(full_api_url)
            if response.status_code == 200:
                return response.json()
            else:
                print("[!] Error: Received non-200 status code from API.")
                return None
        except requests.exceptions.RequestException as e:
            print(f"[!] An error occurred during the request: {e}")
            return None
        except Exception as e:
            print(f"[!] An unexpected error occurred: {e}")
            return None

    def fetch_episodes(self, quality_id):
        try:
            full_api_url = f'{self.base_api_url}moviesdrive/quality?id={quality_id}'
            response = requests.get(full_api_url)
            if response.status_code == 200:
                return response.json()
            else:
                print("[!] Error: Received non-200 status code from API.")
                return None
        except requests.exceptions.RequestException as e:
            print(f"[!] An error occurred during the request: {e}")
            return None
        except Exception as e:
            print(f"[!] An unexpected error occurred: {e}")
            return None

    def fetch_streaminglink(self, url_id):
        try:
            full_api_url = f'{self.base_api_url}moviesdrive/play?id={url_id}'
            response = requests.get(full_api_url)
            if response.status_code == 200 and 'stream' in response.json():
                return response.json()['stream']
            else:
                print("[!] Error: 'stream' key not found in the response or received non-200 status code from API.")
                return None
        except requests.exceptions.RequestException as e:
            print(f"[!] An error occurred during the request: {e}")
            return None
        except Exception as e:
            print(f"[!] An unexpected error occurred: {e}")
            return None
