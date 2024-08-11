from pyfzf.pyfzf import FzfPrompt
from spycli.utils.routes.moviesdrive.fetch import MoviesDriveAPI
from spycli.utils.helper.player import ply
import re
from spycli.utils.core.update import check_for_updates

api = MoviesDriveAPI()

def clean_title(title):
    title = re.sub(r'\[?\s*Download\s*\]?', '', title, flags=re.IGNORECASE)
    title = re.sub(r'(\(.*?\)).*', r'\1', title).strip()
    return title.strip() 

def p_search_results(result_data):
    if not result_data:
        return None, None
    fzf = FzfPrompt()
    movies_list = [clean_title(movie['title']) for movie in result_data]
    selected_strings = fzf.prompt(movies_list)
    if selected_strings:
        selected_index = movies_list.index(selected_strings[0])
        selected_movie = result_data[selected_index]
        return selected_movie['id'],clean_title(selected_movie['title'])
    else:
        return None, None

def p_movies(movie_dict):
    fzf = FzfPrompt()
    if not movie_dict:
        return None
    titles = list(movie_dict.keys())
    selected_title = fzf.prompt(titles)
    if not selected_title:
        return None
    selected_title = selected_title[0]
    return movie_dict[selected_title]

def p_episode(movie_dict):
    fzf = FzfPrompt()
    if not movie_dict:
        return None, None, None
    titles = list(movie_dict.keys())
    selected_title = fzf.prompt(titles)
    if not selected_title:
        return None, None, None
    selected_title = selected_title[0]
    index_of_selected_ep = titles.index(selected_title)
    return index_of_selected_ep, movie_dict[selected_title], selected_title

def p_series(series_dict, selecting_season=True, selected_season=None):
    fzf = FzfPrompt()
    if selecting_season:
        seasons_and_resolutions = list(series_dict.keys())
        if not seasons_and_resolutions:
            return None
        selected_season_resolution = fzf.prompt(seasons_and_resolutions)
        if selected_season_resolution:
            return p_series(series_dict, selecting_season=False, selected_season=selected_season_resolution[0])
        else:
            return None
    else:
        if selected_season not in series_dict:
            return None
        episodes = list(series_dict[selected_season].keys())
        if not episodes:
            return None
        selected_episode = fzf.prompt(episodes)
        if selected_episode:
            episode_identifier = series_dict[selected_season][selected_episode[0]]
            return episode_identifier
        else:
            return None

def check_p_type(parsed_content):
    data = parsed_content['data']
    typecheck = parsed_content['type']
    if typecheck == 'series':
        return p_series(data), typecheck
    elif typecheck == 'movie':
        return p_movies(data), typecheck
    else:
        return None, None
    
    
def get_streaming_id(streaming_id,with_space="HubCloud [Instant DL]",without_space="HubCloud[Instant DL]"):
    parse_streaming_id = streaming_id.get(with_space) or streaming_id.get(without_space)
    if parse_streaming_id:
        hcloud_id = parse_streaming_id.replace("https://hubcloud.lol/video/", "")
        return hcloud_id
    else:
        return None

def gdtot_download_link(gdtot_link):
    print("[!] This is only downloadable content")
    print(f"\033]8;;{gdtot_link}\033\\-------------------------\n- Tap to download -\n-------------------------\033]8;;\033\\\n")
    input("[^] Press Enter to continue...")
    
def movies_player_function(current_playing,streaming_link):
    ply(streaming_link,current_playing)
    fzf = FzfPrompt()
    commands = ["Quit", "Search", "Download"]
    try:
        while True:
            fzf_result = fzf.prompt(commands, "--cycle")

            if not fzf_result:
                break
            else:
                choice = fzf_result[0]

            if choice == "Quit":
                print("[!] Quiting spycli-md...")
                return 'quit'
            elif choice == "Search":
                print("[^] Initiating search...")
                return 'search'
            elif choice == "Download":
                print(f"\033]8;;{streaming_link}\033\\-------------------------\n- Tap to download -\n-------------------------\033]8;;\033\\\n")
                input("[^] Press Enter to continue...")
    except KeyboardInterrupt:
        print("\n[!] Quitting spycli-md...")

def series_player_function(current_playing,streaming_link,current_index, episodes, selected_name):
    ply(streaming_link, current_playing)
    fzf = FzfPrompt()
    commands_base = ["Quit", "Search", "Download"]
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
            dynamic_commands.append(f"Playing {current_episode_key} of {episode_keys[-1]}")

            fzf_result = fzf.prompt(dynamic_commands, "--cycle")

            if not fzf_result:
                break
            else:
                choice = fzf_result[0]

            if choice == "Quit":
                print("[!] Quiting spycli-md...")
                return 'quit'
            elif choice == "Search":
                print("[^] Initiating search...")
                return 'search'
            elif choice == "Download":
                print(f"\033]8;;{streaming_link}\033\\-------------------------\n- Tap to download -\n-------------------------\033]8;;\033\\\n")
                input("[^] Press Enter to continue...")
            elif choice == "Next Episode":
                if current_episode_index < len(episodes) - 1:
                    current_episode_index += 1
                    current_episode_key = episode_keys[current_episode_index]
                    streaming_id = get_streaming_id(episodes[current_episode_key])
                    streaming_link = api.fetch_streaminglink(streaming_id)
                    current_playing = selected_name + " - " + current_episode_key
                    ply(streaming_link,current_playing)
            elif choice == "Previous Episode":
                if current_episode_index > 0:
                    current_episode_index -= 1
                    current_episode_key = episode_keys[current_episode_index]
                    streaming_id = get_streaming_id(episodes[current_episode_key])
                    streaming_link = api.fetch_streaminglink(streaming_id)
                    current_playing = selected_name + " - " + current_episode_key
                    ply(streaming_link,current_playing)
    except KeyboardInterrupt:
        print("\n[!] Quiting spycli-md...")
        
#MAIN FUNCTION
def start_md():
    check_for_updates()
    try:
        while True:
            search_query = input("\033[94mEnter Search: \033[0m")
            if not search_query:
                print("[!] No search query entered. Please enter a search query.")
                continue
            
            search_item = api.search(search_query)
            if not search_item:
                print("[!] Failed to fetch search results.")
                continue

            selected_id, selected_name = p_search_results(search_item)
            if not selected_id:
                print("[!] No streaming sources found.")
                continue

            detail_id = api.fetch_details(selected_id)
            if not detail_id:
                print("[!] Failed to fetch details for the selected item.")
                continue

            quality_id, result_type = check_p_type(detail_id)
            if not quality_id:
                print("[!] You forget to select.")
                continue

            raw_streaming_id = api.fetch_quality(quality_id)
            if result_type == "series":
                selected_ep_index, selected_episode_id, selected_episode = p_episode(raw_streaming_id)
                if selected_episode_id is None:
                    print("[!] No episode was selected.")
                    continue

                if 'gdtot' in selected_episode_id:
                    gdtot_download_link(selected_episode_id)
                    continue

                streaming_id = get_streaming_id(selected_episode_id)
                if not streaming_id:
                    print("[!] No streaming sources found.")
                    continue

                streaming_link = api.fetch_streaminglink(streaming_id)
                current_playing = selected_name + " - " + selected_episode
                what_next = series_player_function(current_playing,streaming_link, selected_ep_index, raw_streaming_id, selected_name)

            elif result_type == "movie":
                streaming_id = get_streaming_id(raw_streaming_id)
                if not streaming_id:
                    print("[!] No streaming sources found.")
                    continue

                streaming_link = api.fetch_streaminglink(streaming_id)
                what_next = movies_player_function(selected_name,streaming_link)
                
            if what_next == "quit":
                break
            elif what_next == "search":
                continue

    except KeyboardInterrupt:
        print("\n[!] Quiting spycli-md...")
