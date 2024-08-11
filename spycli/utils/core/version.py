import os
import json

def get_version():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    version_file_path = os.path.join(base_dir, 'version.json')

    with open(version_file_path, 'r') as file:
        version_data = json.load(file)
        version = version_data['version']
    
    return print("[^] SPYCLI Version:", version)
