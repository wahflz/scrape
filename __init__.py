import yaml
import pathlib
import platform

# CONSTANTS

APP_DIR = pathlib.Path(__file__).resolve().parent
BIN_DIR = APP_DIR / 'bin'
APP_BIN = None

match platform.machine().lower():
    case 'amd64':
        BIN_DIR = BIN_DIR / 'amd64'
    case 'x86_64':
        BIN_DIR = BIN_DIR / 'amd64'
    case _:
        raise OSError('Unsupported architecture')
    
match platform.system().lower():
    case 'windows':
        APP_BIN = BIN_DIR / 'windows' / 'geckodriver.exe'
    case 'linux':
        APP_BIN = BIN_DIR / 'linux' / 'geckodriver'
    case _:
        raise OSError('Unsupported operating system')

# FUNCTIONS

def load_yaml_config(fp):
    with open(fp, 'r') as f:
        config = yaml.safe_load(f)
    return config