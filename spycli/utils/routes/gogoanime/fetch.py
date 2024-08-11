from spycli.utils.helper.getapi import fetch_api
import requests

class GogoAnimeClient:
    def __init__(self):
        self.base_api_url = fetch_api()
        if not self.base_api_url:
            print("[!] Something went wrong with API, please contact the developer.")
            exit(1)

    def fetch_api(self, url):
        try:
            response = requests.get(url)
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
            
    def search_anime(self, search_query):
        search_results = {}
        search_route = f"{self.base_api_url}gogoanime/search?query={search_query}"
        fetched_results = self.fetch_api(search_route)
        if fetched_results is not None:
            if 'results' in fetched_results:
                for result in fetched_results['results']:
                    title = result.get('title', '')
                    identifier = result.get('id', '')
                    search_results[title] = identifier
            return search_results
        else:
            return None

    def get_anime(self, anime_id):
        detail_route = f"{self.base_api_url}gogoanime/detail?id={anime_id}"
        fetched_results = self.fetch_api(detail_route)
        if fetched_results is not None:
            details_data = fetched_results.get('results', {}).get('episodes', '')
            if isinstance(details_data, list) and details_data:
                anime_details = {f"Episode {episode[0]}": episode[1] for episode in details_data}
                return anime_details
            else:
                return None
        else: 
            return None
            
    
    def stream_anime(self, episode_id):
        streaming_route = f"{self.base_api_url}gogoanime/episode?id={episode_id}"
        fetched_results = self.fetch_api(streaming_route)
        if fetched_results is not None:
            sources_data = []
            primary_sources = fetched_results.get('results', {}).get('stream', {}).get('sources', [])
            backup_sources = fetched_results.get('results', {}).get('stream', {}).get('sources_bk', [])
            sources_data.extend(primary_sources + backup_sources)
            streaming_sources = {f"Source {index + 1}": source['file']
                                for index, source in enumerate(sources_data)
                                if source.get('file', '').endswith('.m3u8')}
            return streaming_sources
        else:
            return None

    def download_anime(self, episode_id):
        streaming_route = f"{self.base_api_url}gogoanime/episode/download?id={episode_id}"
        fetched_results = self.fetch_api(streaming_route)
        if fetched_results is not None:
            download_sources = fetched_results.get('results', {})
            if download_sources:
                return download_sources
            else:
                return None
        else:
            return None
