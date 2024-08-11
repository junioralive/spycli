from pyfzf.pyfzf import FzfPrompt
from spycli.utils.routes.tmdb.tmdb import TMDBClient
from spycli.utils.routes.vidsrc.fetch import AIOSClient
from spycli.utils.helper.player import ply
import re
from spycli.utils.core.update import check_for_updates

tmdb_client = TMDBClient()
aios_client = AIOSClient()

def prompt_search(data):
    fzf = FzfPrompt()
    options = list(data.keys())
    result = fzf.prompt(options, "--cycle")
    selected_key = result[0] if result else None
    if selected_key:
        format_name = format_title(selected_key)
        return format_name, data[selected_key]
    else:
        return None, None


def prompt_episode(seasons_episodes):
    fzf = FzfPrompt()
    while True:
        seasons = list(seasons_episodes.keys())
        selected_season = fzf.prompt(seasons, "--cycle")[0]
        while True:
            episodes = ['back'] + seasons_episodes[selected_season]
            selected_episode_str = fzf.prompt(episodes, "--cycle")[0]
            if selected_episode_str == 'back':
                break
            selected_episode = int(selected_episode_str.split(' ')[-1])
            return selected_season, selected_episode

def switch_source(data):
    if not data:
        return None
    fzf = FzfPrompt()
    options = list(data.keys())
    selected_key = fzf.prompt(options, "--cycle")[0]
    return data[selected_key]

def format_title(text):
    formatted_title = re.sub(r'\(.*?\)', '', text)
    return formatted_title.strip()

def check_type(url):
    if "tv" in url:
        streamlink, season_episode_data, season, current_index, current_episode  = format_series_route(url)
        return streamlink, "tv", season_episode_data, season, current_index, current_episode
    elif "movie" in url:
        streamlink = format_movie_route(url)
        return streamlink, "movie", None, None, 0, None
    else:
        return None, None, None, None, None, None

def format_series_route(apiurl):
    seasons_episodes, tmdb_id = tmdb_client.get_details(apiurl)
    if isinstance(seasons_episodes, dict):
        season, episode = prompt_episode(seasons_episodes)
        current_index = int(episode) - 1
        current_episode = f"Episode {episode}"
        format_season = re.findall(r'\d+', season)[0]
        route_url = f"tv?id={tmdb_id}&season={format_season}&episode={episode}"
        return route_url, seasons_episodes, season, current_index, current_episode
    else:
        return None, None

def format_movie_route(apiurl):
    if isinstance(apiurl, str):
        tmdb_id = apiurl.replace("/movie/", "")
        api_formatted_url = f"movie?id={tmdb_id}"
        return api_formatted_url
    else:
        return None

def generate_episode_routes(data, season_number):
    season_data = data[season_number]
    season_number = re.findall(r'\d+', season_number)[0]
    base_url = "tv?id=1396&season={}&episode={}"
    episode_urls = {episode: base_url.format(season_number, i + 1) for i, episode in enumerate(season_data)}
    return episode_urls

def generate_movie_routes(movie_name, movie_dict):
     return {movie_name: movie_dict}

# -----------------------------
#           VIDSRC   
# -----------------------------

def vidsrc_player_function(current_playing, ms_name, streaming_link, subtitles_links, current_index, episodes):
    ply(streaming_link, current_playing, subtitles_links)

    fzf = FzfPrompt()
    commands_base = ["Quit", "Search"]
    current_episode_index = current_index

    try:
        while True:
            episode_keys = list(episodes.keys())
            current_episode_key = episode_keys[current_episode_index]
            dynamic_commands = commands_base.copy()

            if current_episode_index < len(episodes) - 1:
                dynamic_commands.append("Next Episode")
            if current_episode_index > 0:
                dynamic_commands.append("Previous Episode")
            if current_episode_index < len(episodes) - 1 or current_episode_index > 0:
                dynamic_commands.append(f"Playing {current_episode_key} of {episode_keys[-1]}")

            fzf_result = fzf.prompt(dynamic_commands, "--cycle")

            if not fzf_result:
                break
            else:
                choice = fzf_result[0]
                
            if choice == "Quit":
                print("[!] Quitting spycli-vidsrc...")
                return 'quit'
            elif choice == "Search":
                print("[^] Initiating search...")
                return 'search'
            elif choice == "Next Episode":
                if current_episode_index < len(episodes) - 1:
                    current_episode_index += 1
                    current_episode_key = episode_keys[current_episode_index]
                    episode_id = episodes[current_episode_key]
                    fetch_links = aios_client.get_vidsrc_stream(episode_id)
                    if not fetch_links:
                        print("[!] Source not found.")
                        continue
                    default_source = next(iter(fetch_links.values()))
                    streaming_link, subtitles_links = aios_client.format_subtitles(default_source)
                    current_playing = ms_name + " - " + current_episode_key
                    ply(streaming_link, current_playing, subtitles_links)
            elif choice == "Previous Episode":
                if current_episode_index > 0:
                    current_episode_index -= 1
                    current_episode_key = episode_keys[current_episode_index]
                    episode_id = episodes[current_episode_key]
                    fetch_links = aios_client.get_vidsrc_stream(episode_id)
                    if not fetch_links:
                        print("[!] Source not found.")
                        continue
                    default_source = next(iter(fetch_links.values()))
                    streaming_link, subtitles_links = aios_client.format_subtitles(default_source)
                    current_playing = ms_name + " - " + current_episode_key
                    ply(streaming_link, current_playing, subtitles_links)
    except KeyboardInterrupt:
        print("\n[!] Quitting spycli-vidsrc...")

def start_vidsrc():
    check_for_updates()
    try:
        while True:
            search_query = input("\033[91mEnter Search: \033[0m")
            
            if not search_query:
                print("[!] No search query entered. Please enter a search query.")
                continue

            search_item = tmdb_client.search(search_query)
            if not search_item:
                print("[!] Failed to fetch search results.")
                continue

            selected_name, selected_item = prompt_search(search_item)
            if not selected_item:
                print("[!] No selection made.")
                continue

            vidsrc_route, link_type, season_episode_data, season_no, current_index, current_episode  = check_type(selected_item)
            
            if not vidsrc_route:
                print("[!] Something went wrong building route.")
                continue

            if link_type == 'movie':
                fetch_links = aios_client.get_vidsrc_stream(vidsrc_route)
                print(fetch_links)
                input("Press Enter to continue...")
                if not fetch_links:
                    print("[!] Source not found.")
                    continue
                
                movie_data = generate_movie_routes(selected_name, vidsrc_route)
                default_source = next(iter(fetch_links.values()))
                streaming_link, subtitles_links = aios_client.format_subtitles(default_source)
                vidsrc_player_function(selected_name, selected_name, streaming_link, subtitles_links, current_index, movie_data)
                
            elif link_type == 'tv':
                fetch_links = aios_client.get_vidsrc_stream(vidsrc_route)
                if not fetch_links:
                    print("[!] Source not found.")
                    continue
                
                episode_data = generate_episode_routes(season_episode_data, season_no)
                default_source = next(iter(fetch_links.values()))
                streaming_link, subtitles_links = aios_client.format_subtitles(default_source)
                current_playing = selected_name + " - " + current_episode
                vidsrc_player_function(current_playing, selected_name, streaming_link, subtitles_links, current_index, episode_data)
    except KeyboardInterrupt:
        print("\n[!] Quitting spycli-vidsrc...")

# -----------------------------
#           FLIXHQ  
# -----------------------------

def flixhq_player_function(current_playing, ms_name, streaming_link, subtitles_links, current_index, episodes):
    ply(streaming_link, current_playing, subtitles_links)

    fzf = FzfPrompt()
    commands_base = ["Quit", "Search"]
    current_episode_index = current_index

    try:
        while True:
            episode_keys = list(episodes.keys())
            current_episode_key = episode_keys[current_episode_index]
            dynamic_commands = commands_base.copy()

            if current_episode_index < len(episodes) - 1:
                dynamic_commands.append("Next Episode")
            if current_episode_index > 0:
                dynamic_commands.append("Previous Episode")
            if current_episode_index < len(episodes) - 1 or current_episode_index > 0:
                dynamic_commands.append(f"Playing {current_episode_key} of {episode_keys[-1]}")

            fzf_result = fzf.prompt(dynamic_commands, "--cycle")

            if not fzf_result:
                break
            else:
                choice = fzf_result[0]
                
            if choice == "Quit":
                print("[!] Quitting spycli-flixhq...")
                return 'quit'
            elif choice == "Search":
                print("[^] Initiating search...")
                return 'search'
            elif choice == "Next Episode":
                if current_episode_index < len(episodes) - 1:
                    current_episode_index += 1
                    current_episode_key = episode_keys[current_episode_index]
                    episode_id = episodes[current_episode_key]
                    fetch_links = aios_client.get_flixhq_stream(episode_id)
                    if not fetch_links:
                        print("[!] Source not found.")
                        continue
                    default_source = next(iter(fetch_links.values()))
                    streaming_link, subtitles_links = aios_client.format_subtitles(default_source)
                    current_playing = ms_name + " - " + current_episode_key
                    ply(streaming_link, current_playing, subtitles_links)
            elif choice == "Previous Episode":
                if current_episode_index > 0:
                    current_episode_index -= 1
                    current_episode_key = episode_keys[current_episode_index]
                    episode_id = episodes[current_episode_key]
                    fetch_links = aios_client.get_flixhq_stream(episode_id)
                    if not fetch_links:
                        print("[!] Source not found.")
                        continue
                    default_source = next(iter(fetch_links.values()))
                    streaming_link, subtitles_links = aios_client.format_subtitles(default_source)
                    current_playing = ms_name + " - " + current_episode_key
                    ply(streaming_link, current_playing, subtitles_links)
    except KeyboardInterrupt:
        print("\n[!] Quitting spycli-flixhq...")

def start_flixhq():
    check_for_updates()
    try:
        while True:
            search_query = input("\033[91mEnter Search: \033[0m")
            
            if not search_query:
                print("[!] No search query entered. Please enter a search query.")
                continue

            search_item = tmdb_client.search(search_query)
            if not search_item:
                print("[!] Failed to fetch search results.")
                continue

            selected_name, selected_item = prompt_search(search_item)
            if not selected_item:
                print("[!] No selection made.")
                continue

            vidsrc_route, link_type, season_episode_data, season_no, current_index, current_episode  = check_type(selected_item)
            
            if not vidsrc_route:
                print("[!] Something went wrong building route.")
                continue
            
            if link_type == 'movie':
                fetch_links = aios_client.get_flixhq_stream(vidsrc_route)
                if not fetch_links:
                    print("[!] Source not found.")
                    continue
                
                movie_data = generate_movie_routes(selected_name, vidsrc_route)
                default_source = next(iter(fetch_links.values()))
                streaming_link, subtitles_links = aios_client.format_subtitles(default_source)
                flixhq_player_function(selected_name, selected_name, streaming_link, subtitles_links, current_index, movie_data)
                
            elif link_type == 'tv':
                fetch_links = aios_client.get_flixhq_stream(vidsrc_route)
                if not fetch_links:
                    print("[!] Source not found.")
                    continue
                
                episode_data = generate_episode_routes(season_episode_data, season_no)
                default_source = next(iter(fetch_links.values()))
                streaming_link, subtitles_links = aios_client.format_subtitles(default_source)
                current_playing = selected_name + " - " + current_episode
                flixhq_player_function(current_playing, selected_name, streaming_link, subtitles_links, current_index, episode_data)
    except KeyboardInterrupt:
        print("\n[!] Quitting spycli-flixhq...")
