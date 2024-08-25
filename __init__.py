import yaml
import shutil
import pathlib

# CONSTANTS

APP_DIR = pathlib.Path(__file__).resolve().parent
BIN_DIR = APP_DIR / 'geckodriver'
APP_BIN = shutil.which('geckodriver')

if APP_BIN is None:
    raise OSError('geckodriver bin must be in PATH or CWD')

# FUNCTIONS

def load_yaml_config(fp):
    with open(fp, 'r') as f:
        config = yaml.safe_load(f)
    return config
