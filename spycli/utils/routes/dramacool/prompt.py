from spycli.utils.helper.player import ply
from pyfzf.pyfzf import FzfPrompt
from spycli.utils.routes.dramacool.fetch import DramaCoolClient
from spycli.utils.core.update import check_for_updates

client = DramaCoolClient()

def search_select_item(search_query):
    fzf = FzfPrompt()
    current_page = 1
    hasNextPage = True
    hasPrevPage = False
    while True:
        search_results, hasNextPage, hasPrevPage, current_page = client.search_drama(search_query, current_page)
        if not search_results:
            return None, None
        titles = list(search_results.keys())
        if hasPrevPage:
            titles.append("Prev - Show previous page")
        if hasNextPage:
            titles.append("Next - Show next page")
        selected_title = fzf.prompt(titles)
        if not selected_title:
            return None, None
        selected_title = selected_title[0]
        if selected_title.startswith("Next") and hasNextPage:
            current_page += 1
            continue
        elif selected_title.startswith("Prev") and hasPrevPage:
            current_page -= 1
            continue
        elif selected_title in search_results:
            return selected_title, search_results[selected_title]
        else:
            print("[!] Invalid selection. Please try again.")

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
    
def format_single_ep(item_dict):
    if len(item_dict) == 1:
        key = next(iter(item_dict))
        value = item_dict[key]
        index = 0
        return key, value, index
    else:
        return None, None, None

def player_function(current_drama, drama_name, streaming_link, current_index, episodes, drama_id):
    default_source = list(streaming_link.values())[0]
    ply(default_source, current_drama)

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
                print("[!] Quitting spycli-drama...")
                return 'quit'
            elif choice == "Search":
                print("[^] Initiating search...")
                return 'search'
            elif choice == "Next Episode":
                if current_episode_index < len(episodes) - 1:
                    current_episode_index += 1
                    current_episode_key = episode_keys[current_episode_index]
                    episode_id = episodes[current_episode_key]
                    streaming_link = client.stream_drama(episode_id, drama_id)
                    default_source = list(streaming_link.values())[0]
                    current_playing = drama_name + " - " + current_episode_key
                    ply(default_source, current_playing)
            elif choice == "Previous Episode":
                if current_episode_index > 0:
                    current_episode_index -= 1
                    current_episode_key = episode_keys[current_episode_index]
                    episode_id = episodes[current_episode_key]
                    streaming_link = client.stream_drama(episode_id, drama_id)
                    default_source = list(streaming_link.values())[0]
                    current_playing = drama_name + " - " + current_episode_key
                    ply(default_source, current_playing)
    except KeyboardInterrupt:
        print("\n[!] Quitting spycli-drama...")

        
def start_drama():
    check_for_updates()
    try:
        while True:
            search_query = input("\033[95mEnter Drama: \033[0m")
            if not search_query:
                print("[!] No search query entered. Please enter a search query.")
                continue
            drama_name, drama_id = search_select_item(search_query)
            if not drama_id:
                print("[!] Failed to fetch search results.")
                continue

            drama_details = client.get_drama(drama_id)
            if not drama_details:
                print("[!] Failed to fetch details for the selected drama.")
                continue

            if len(drama_details) == 1:
                print("[!] Please wait while we fetch the links...")
                episode_name, episode_id, current_index = format_single_ep(drama_details)
            else:
                episode_name, episode_id, current_index = prompt_episode(drama_details)

            if not episode_id or current_index is None:
                print("[!] No episode selected.")
                continue

            streaming_link = client.stream_drama(episode_id, drama_id)
            current_drama = drama_name + (" - " + episode_name if len(drama_details) > 1 else "")
            what_next = player_function(current_drama, drama_name, streaming_link, current_index, drama_details, drama_id)

            if what_next == 'quit':
                break
            elif what_next == 'search':
                continue

    except KeyboardInterrupt:
        print("\n[!] Quitting spycli-drama...")
