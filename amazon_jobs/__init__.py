import pathlib
import logging
from .. import load_yaml_config

# CONSTANTS

AMAZON_JOBS_DIR = pathlib.Path(__file__).resolve().parent

# CONFIGURATION

AMAZON_JOBS_CONFIG = load_yaml_config(AMAZON_JOBS_DIR / 'config.yml')

if 'amazon' not in AMAZON_JOBS_CONFIG:
    raise RuntimeError('Amazon configuration missing')

if 'zips' not in AMAZON_JOBS_CONFIG['amazon']:
    raise RuntimeError('Amazon configuration requires a zip code')

logger = logging.getLogger('Amazon_Jobs')
logger.setLevel(logging.INFO)
