from spycli.utils.routes.gogoanime.fetch import GogoAnimeClient
from spycli.utils.helper.player import ply
from pyfzf.pyfzf import FzfPrompt
from spycli.utils.core.update import check_for_updates
  
client = GogoAnimeClient()

def format_search_results(search_item, key_options):
    results = {}
    for key in key_options:
        if key in search_item:
            results[key] = search_item[key]
    return results

def p_search_results(search_item):
    fzf = FzfPrompt()
    if not search_item:
        return None, None
    titles = list(search_item.keys())
    selected_title = fzf.prompt(titles)
    if not selected_title:
        return None, None
    selected_title = selected_title[0]
    return selected_title, search_item[selected_title]

def p_download(episode_result):
    fzf = FzfPrompt()
    chosen_keys = fzf.prompt(list(episode_result.keys()), "--cycle")
    if chosen_keys:
        chosen_key = chosen_keys[0]
        if chosen_key in episode_result:
            chosen_url = episode_result[chosen_key]
            return chosen_url
        else:
            return None
    else:
        return None
    
def prompt_episode(episode_result):
    fzf = FzfPrompt()
    chosen_keys = fzf.prompt(list(episode_result.keys()), "--cycle")
    if chosen_keys:
        chosen_key = chosen_keys[0]
        if chosen_key in episode_result:
            chosen_url = episode_result[chosen_key]
            index = list(episode_result.keys()).index(chosen_key)
            return chosen_key, chosen_url, index
        else:
            return None, None, None
    else:
        return None, None, None

def download_function(episode_id):
    get_download_links = client.download_anime(episode_id)
    if get_download_links is not None:
        chosen_url = p_download(get_download_links)
        print(f"\033]8;;{chosen_url}\033\\-------------------------\n- Tap to download -\n-------------------------\033]8;;\033\\\n")
        input("[^] Press Enter to continue...")

def format_single_ep(item_dict):
    if len(item_dict) == 1:
        key = next(iter(item_dict))
        value = item_dict[key]
        index = 0
        return key, value, index
    else:
        return None, None, None

def player_function(current_anime, anime_name, streaming_link, current_index, episodes, anime_id):
    default_source = list(streaming_link.values())[0]
    ply(default_source, current_anime)

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
            if current_episode_index < len(episodes) - 1 or current_episode_index > 0:
                dynamic_commands.append(f"Playing {current_episode_key} of {episode_keys[-1]}")

            fzf_result = fzf.prompt(dynamic_commands, "--cycle")

            if not fzf_result:
                break
            else:
                choice = fzf_result[0]

            if choice == "Quit":
                print("[!] Quitting spycli-anime...")
                return 'quit'
            elif choice == "Search":
                print("[^] Initiating search...")
                return 'search'
            elif choice == "Download":
                episode_id = episodes[current_episode_key]
                download_function(episode_id)
            elif choice == "Next Episode":
                if current_episode_index < len(episodes) - 1:
                    current_episode_index += 1
                    current_episode_key = episode_keys[current_episode_index]
                    episode_id = episodes[current_episode_key]
                    streaming_link = client.stream_anime(episode_id)
                    default_source = list(streaming_link.values())[0]
                    current_playing = anime_name + " - " + current_episode_key
                    ply(default_source, current_playing)
            elif choice == "Previous Episode":
                if current_episode_index > 0:
                    current_episode_index -= 1
                    current_episode_key = episode_keys[current_episode_index]
                    episode_id = episodes[current_episode_key]
                    streaming_link = client.stream_anime(episode_id)
                    default_source = list(streaming_link.values())[0]
                    current_playing = anime_name + " - " + current_episode_key
                    ply(default_source, current_playing)
    except KeyboardInterrupt:
        print("\n[!] Quitting spycli-anime...")
        
def start_anime():
    check_for_updates()
    try:
        while True:
            search_query = input("\033[95mEnter Anime: \033[0m")
            search_item = client.search_anime(search_query)
            if not search_item:
                print("[!] No search query entered. Please enter a search query.")
                continue
            anime_name, anime_id = p_search_results(search_item)
            if not anime_id:
                print("[!] Failed to fetch search results.")
                continue

            anime_details = client.get_anime(anime_id)
            if not anime_details:
                print("[!] Failed to fetch details for the selected anime.")
                continue

            if len(anime_details) == 1:
                print("[!] Please wait while we fetch the links...")
                episode_name, episode_id, current_index = format_single_ep(anime_details)
            else:
                episode_name, episode_id, current_index = prompt_episode(anime_details)

            if not episode_id or current_index is None:
                print("[!] No episode selected.")
                continue

            streaming_link = client.stream_anime(episode_id)
            current_anime = anime_name + (" - " + episode_name if len(anime_details) > 1 else "")
            what_next = player_function(current_anime, anime_name, streaming_link, current_index, anime_details, anime_id)

            if what_next == 'quit':
                break
            elif what_next == 'search':
                continue

    except KeyboardInterrupt:
        print("\n[!] Quitting spycli-anime...")
