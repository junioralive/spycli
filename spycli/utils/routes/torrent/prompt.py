import webbrowser
from pyfzf.pyfzf import FzfPrompt
from spycli.utils.routes.torrent.fetch import TorrentFetch
from spycli.utils.core.update import check_for_updates

torrent_fetcher = TorrentFetch()

def pyfzf_select(keys):
    fzf = FzfPrompt()
    selected_key = fzf.prompt(keys)
    return selected_key[0] if selected_key else None

def start_torrent():
    check_for_updates()
    try:
        while True:
            search_query = input("Enter Search: ")
            formatted_data = torrent_fetcher.search_site(search_query,'1337x')
            if formatted_data:
                selected_key = pyfzf_select(list(formatted_data.keys()))
                if selected_key is not None:
                    selected_link = formatted_data.get(selected_key)
                    if selected_link is not None:
                        print("[^] Downloading...")
                        webbrowser.open(selected_link)
                    else:
                        print("[!] No link found for the selected Item.")
                else:
                    print("[!] No item selected.")
            else:
                print("[!] Failed to fetch search results.")
    except KeyboardInterrupt:
        print("\n[!] Quitting spycli-torrent...")
