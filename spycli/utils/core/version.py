import os
import json

def get_version():
    version_file_path = os.path.join(os.path.dirname(__file__), 'version.json')

    with open(version_file_path, 'r') as file:
        version_data = json.load(file)
        version = version_data['version']
    
    return print("[^] SPYCLI Version:", version)
