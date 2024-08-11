import requests
from spycli.utils.helper.getapi import fetch_api

class TorrentFetch:  
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
                format_response = self.format_response_results(response.json())
                return format_response
            else:
                print(f"[!] Error: Received {response.status_code} status code from API.")
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

    def format_response_results(self, data):
        if data is not None:
            formatted_data = {}
            for item in data["data"]:
                name = item["name"]
                size = item.get("size", "NA")
                category = item.get("category", "NA")
                if "magnet" in item:
                    link = item["magnet"]
                elif "torrent" in item:
                    link = item["torrent"]
                else:
                    link = item["url"]
                formatted_key = f"{name} - {size} - {category}"
                formatted_data[formatted_key] = link
            return formatted_data
        else:
            return None

    def search_all(self, query, page=1, limit=10):
        params = {'query': query, 'page':page, 'limit': limit}
        return self.fetch_api("torrent/search/all", params=params)

    def search_site(self, query, site, page=1, limit=25):
        params = {'query': query, 'site': site, 'page':page, 'limit': limit}
        return self.fetch_api("torrent/search/site", params=params)
