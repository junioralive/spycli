import requests
from spycli.utils.helper.getapi import fetch_api

class DramaCoolClient:
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
            
    def search_drama(self, search_query, page=1):
        search_results = {}
        search_route = f"{self.base_api_url}dramacool/search?query={search_query}&page={page}"
        fetched_results = self.fetch_api(search_route)
        if fetched_results is not None:
            if 'results' in fetched_results:
                for result in fetched_results['results']:
                    title = result.get('title', '')
                    identifier = result.get('id', '')
                    search_results[title] = identifier
                current_page = int(fetched_results.get('currentPage', page))
                hasNextPage = fetched_results.get('hasNextPage', False)
                hasPrevPage = current_page > 1
                return search_results, hasNextPage, hasPrevPage, current_page
        else:
            return None, False, False, page

    def get_drama(self, drama_id):
        details_results = {}
        detail_route = f"{self.base_api_url}dramacool/info?id={drama_id}"
        fetched_results = self.fetch_api(detail_route)
        if fetched_results is not None:
            if 'episodes' in fetched_results:
                for result in fetched_results['episodes']:
                    episode_num = result.get('episode', '')
                    title = f"Episode {episode_num}"
                    identifier = result.get('id', '')
                    details_results[title] = identifier
            return details_results
        else:
            return None
            
    def stream_drama(self, episode_id, drama_id):
        streaming_links = {}
        detail_route = f"{self.base_api_url}dramacool/streaming?episodeId={episode_id}&mediaId={drama_id}&server=asianload"
        fetched_results = self.fetch_api(detail_route)
        if fetched_results is not None:
            if 'sources' in fetched_results:
                source_counter = 1
                for source in fetched_results['sources']:
                    if source.get("isM3U8", False):
                        source_title = f"Source {source_counter}"
                        streaming_links[source_title] = source.get("url", "")
                        source_counter += 1 
                return streaming_links
        else:
            return None
