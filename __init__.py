import yaml
import shutil
import pathlib
import platform

# CONSTANTS

APP_DIR = pathlib.Path(__file__).resolve().parent
APP_BIN = shutil.which('geckodriver')

if APP_BIN is None:
    if platform.system() == 'Windows':
        APP_BIN = APP_DIR / 'geckodriver.exe'
    else:
        APP_BIN = APP_DIR / 'geckodriver'

    if not APP_BIN.exists():
        raise OSError('Could not locate geckodriver')

# FUNCTIONS

def load_yaml_config(fp):
    with open(fp, 'r') as f:
        config = yaml.safe_load(f)
    return config
