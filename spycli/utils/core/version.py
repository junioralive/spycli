import importlib.util
import os

def get_version():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    version_file_path = os.path.join(base_dir, '__version__.py')
    spec = importlib.util.spec_from_file_location("version", version_file_path)
    version_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(version_module)
    return print("[^] SPYCLI Version:", version_module.__version__)
