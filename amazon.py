import re
from collections import namedtuple
from . import APP_DIR, load_yaml_config
from .browser import Browser
from .alert import Pushover

config = load_yaml_config(APP_DIR / 'config.yml')

if 'amazon' not in config:
    raise RuntimeError('Amazon configuration missing')

# CONSTANTS

APP_URL = (
    'https://hiring.amazon.com/app#/jobSearch?query='
    f'&postal={config['amazon']['zip']}'
    '&locale=en-US'
)

APP_MAP = {
    'class': {
        'job_item': {
            'self': 'jobCardItem'
        }
    },
    'CSS': {
        'cookies': {
            'consent': '[data-test-id="consentBtn"]'
        },
        'notifications': {
            'close': '[data-test-id="sortCloseModal"]'
        }
    },
    'XPATH': {
        'job_item': {
            'location': './div/div/div[2]/*[last()]/strong' # relative
        }
    }
}

# REGEX PATTERNS

RE_LOCATION = re.compile((
    r'Within (?P<miles>\d+(\.\d+)?) mi \| '
    r'(?P<city>[^,]+), '
    r'(?P<state>[A-Z]{2})'
))

# GLOBAL VARIABLES

jobs = []
JobItem = namedtuple('JobItem', ['miles', 'city', 'state'])

# DEW IT!

with Browser() as wb:
    wb.get(APP_URL)

    wb.jitter(3, 5) # Wait for page to finish loading. There is a cleaner way to handle this.

    wb.clear_form_by_css(APP_MAP['CSS']['cookies']['consent'])
    wb.clear_form_by_css(APP_MAP['CSS']['notifications']['close'])

    wb.jitter(3, 5) # Wait again...

    for item in wb.find_elements_by_class(APP_MAP['class']['job_item']['self']):
        location = wb.find_child_by_xpath(item, APP_MAP['XPATH']['job_item']['location'])

        if match := RE_LOCATION.match(location.text):
            job = JobItem(
                float(match.group('miles')),
                match.group('city'),
                match.group('state')
            )

            if job.miles < config['amazon'].get('distance', 0):
                jobs.append(job)
            elif job.city in config['amazon'].get('cities', []):
                jobs.append(job)

    if not jobs:
        exit()
    
    message = 'The following Amazon jobs are available:\n\n'
    for job in jobs:
        message += f"{job.miles} mi | {job.city}, {job.state}\n"

    with Pushover(config['pushover']['api_key'], config['pushover']['user_key']) as p:
        p.message(message)
