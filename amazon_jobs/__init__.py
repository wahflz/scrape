import pathlib
from .. import load_yaml_config

# CONSTANTS

AMAZON_JOBS_DIR = pathlib.Path(__file__).resolve().parent

# CONFIGURATION

AMAZON_JOBS_CONFIG = load_yaml_config(AMAZON_JOBS_DIR / 'config.yml')

if 'amazon' not in AMAZON_JOBS_CONFIG:
    raise RuntimeError('Amazon configuration missing')

if 'zips' not in AMAZON_JOBS_CONFIG['amazon']:
    raise RuntimeError('Amazon configuration requires a zip code')

# if all(k not in AMAZON_JOBS_CONFIG['amazon'] for k in ('distance', 'cities')):
#     raise RuntimeError('Amazon configuration requires search criteria')   
