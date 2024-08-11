import requests
from pyfzf.pyfzf import FzfPrompt
from spycli.utils.helper.getapi import fetch_api

class AIOSClient:
    def __init__(self):
        self.base_api_url = fetch_api()
        if not self.base_api_url:
            print("[!] Something went wrong with API, please contact the developer.")
            exit(1)
            
    def get_vidsrc_stream(self, route_endpoint):
        first_route = f"{self.base_api_url}aios/vidsrc/{route_endpoint}"
        print(first_route)
        try:
            response = requests.get(first_route)
            if response.status_code == 200:
                processed_response = self.process_vidsrc_response(response)
                if processed_response:
                    return processed_response
        except requests.exceptions.RequestException as e:
            print(f"[!] Failed to fetch data from VIDSRC: {e}")

        second_route = f"{self.base_api_url}aios/vidsrcme/{route_endpoint}"
        print(second_route)
        try:
            response = requests.get(second_route)
            
            if response.status_code == 200:
                processed_response = self.process_vidsrcme_response(response)
                if processed_response:
                    return processed_response
        except requests.exceptions.RequestException as e:
            print(f"[!] Failed to fetch data from VIDSRCME: {e}")

        return {}


    def process_vidsrc_response(self, response):
        data = response.json()
        print(data)
        if not data:
            return {}

        formatted_data = {}
        stream_sources = data[1].get('data', {}).get('sourcses', [])
        subtitles = data[1].get('data', {}).get('subtitles', [])

        for source in stream_sources:
            if source.get('isM3U8') == "true":
                subtitles_dict = {sub['lang']: sub['url'] for sub in subtitles}
                formatted_data[source['quality']] = {
                    'stream': source['url'],
                    'subtitles': subtitles_dict
                }
        return formatted_data

    def process_vidsrcme_response(self, response):
        data = response.json()
        print(data)
        if not data:
            return {}

        if len(data) < 2:
            return {}

        stream_data = data[1].get('data', {})
        stream_sources = stream_data.get('sources', [])
        subtitles = stream_data.get('subtitles', [])
        subtitles_dict = {sub['lang']: sub['url'] for sub in subtitles}

        formatted_data = {}
        for source in stream_sources:
            if source.get('isM3U8', False):
                formatted_data[source['quality']] = {
                    'stream': source['url'],
                    'subtitles': subtitles_dict
                }
        return formatted_data


    def get_flixhq_stream(self, route_endpoint):
        search_route = f"{self.base_api_url}aios/flixhq/{route_endpoint}"
        try:
            response = requests.get(search_route)
            if response.status_code == 200:
                data = response.json()
                if not data:
                    return {}

                stream_data = data.get('data', {})
                stream_sources = stream_data.get('sources', [])
                subtitles = stream_data.get('subtitles', [])
                formatted_data = {}
                for source in stream_sources:
                    if source.get('isM3U8', False) and source['quality'] == "auto":
                        subtitles_dict = {sub['lang']: sub['url'] for sub in subtitles}
                        formatted_data['HLS'] = {
                            'stream': source['url'],
                            'subtitles': subtitles_dict
                        }
                return formatted_data
            else:
                print(f"[!] Bad response status: {response.status_code}")
                return {}
        except requests.exceptions.RequestException as e:
            print(f"[!] Failed to fetch data due to an exception: {e}")
            return {}
        
    def format_subtitles(self, data):
        stream_url = data.get('stream')
        if not stream_url:
            return None, None
        
        subtitles = data.get('subtitles', {})
        if not subtitles:
            return stream_url, None

        if len(subtitles) == 1:
            selected_language = next(iter(subtitles))
        else:
            selected_language = self.select_subtitle_language(list(subtitles.keys()))

        selected_subtitle_url = subtitles[selected_language]
        return stream_url, selected_subtitle_url

    def select_subtitle_language(self, options):
        fzf = FzfPrompt()
        return fzf.prompt(options, "--cycle")[0]
