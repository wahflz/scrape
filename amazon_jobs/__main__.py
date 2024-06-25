import re
from collections import namedtuple
from datetime import datetime, timedelta
from . import AMAZON_JOBS_CONFIG as CFG
from ..alert import Pushover
from ..browser import Browser

# CONSTANTS

AMAZON_JOBS_URL = (
    'https://hiring.amazon.com/app#/jobSearch?'
    f'postal={CFG["amazon"]["zip"]}'
    '&locale=en-US'
)

# REGEX PATTERNS

RE_LOCATION = re.compile((
    r'Within (?P<miles>\d+(\.\d+)?) mi \| '
    r'(?P<city>[^,]+), '
    r'(?P<state>[A-Z]{2})'
))

# GLOBAL VARIABLES

jobs = []
JobItem = namedtuple('JobItem', ['miles', 'city', 'state'])

# CACHE

min_time = timedelta(days=1)

# DEW IT!

with Browser() as wb:
    wb.get(AMAZON_JOBS_URL)

    wb.jitter(3, 5) # Wait for page to finish loading. There is a cleaner way to handle this.

    wb.clear_form_by_css('[data-test-id="consentBtn"]') # cookies
    wb.clear_form_by_css('[data-test-id="sortCloseModal"]') # notifications

    wb.jitter(3, 5) # Wait again...

    for item in wb.find_elements_by_class('jobCardItem'):
        location = wb.find_child_by_xpath(item, './div/div/div[2]/*[last()]/strong')

        if match := RE_LOCATION.match(location.text):
            now = datetime.now()
            job = JobItem(
                float(match.group('miles')),
                match.group('city'),
                match.group('state')
            )

            if (
                job.miles < CFG['amazon'].get('distance', 0) or
                job.city in CFG['amazon'].get('cities', [])
            ):
                jobs.append(job)

    if not jobs:
        exit()

    content = ''
    for j in jobs:
        content += f"✅ {j.city}, {j.state} ({j.miles} mi)\n"

    with Pushover(CFG['pushover']['api_key'], CFG['pushover']['user_key']) as p:
        p.message(content)
