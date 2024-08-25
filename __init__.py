import yaml
import shutil
import pathlib
import platform

# CONSTANTS

APP_DIR = pathlib.Path(__file__).resolve().parent
BIN_DIR = APP_DIR / 'geckodriver'
APP_BIN = shutil.which('geckodriver')

if APP_BIN is None:
    match platform.system().lower():
        case 'windows':
            APP_BIN = BIN_DIR / 'windows' / 'geckodriver.exe'
        case 'linux':
            APP_BIN = BIN_DIR / 'linux' / 'geckodriver'
        case _:
            raise OSError('Unsupported operating system')

    raise OSError('geckodriver bin must be in PATH or CWD')

# FUNCTIONS

def load_yaml_config(fp):
    with open(fp, 'r') as f:
        config = yaml.safe_load(f)
    return config
