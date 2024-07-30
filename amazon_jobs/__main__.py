import re
from collections import namedtuple
from string import Template
from . import AMAZON_JOBS_CONFIG as CFG
from ..alert import Pushover
from ..browser import Browser

# CONSTANTS

AMAZON_JOBS_URL = Template(
    'https://hiring.amazon.com/app#/jobSearch?'
    'postal=$postal'
    '&locale=en-US'
)

# REGEX PATTERNS

RE_LOCATION = re.compile((r'(?P<city>[^\n]+),\s(?P<state>[A-Z]{2})$'))

# GLOBAL VARIABLES

jobs = []
JobItem = namedtuple('JobItem', ['position', 'city', 'state'])

# DEW IT!

with Browser() as wb:
    for zip in CFG['amazon'].get('zips', []):
        wb.get(AMAZON_JOBS_URL.substitute(postal=zip))

        wb.jitter(3, 5)

        wb.clear_form_by_css('[data-test-id="consentBtn"]') # cookies
        wb.clear_form_by_css('[data-test-id="sortCloseModal"]') # notifications

        wb.jitter(3, 5)

        for item in wb.find_elements_by_class('jobCardItem'):
            position = wb.find_child_by_xpath(item, './div/div/div[2]/div[1]').text
            location = wb.find_child_by_xpath(item, './div/div/div[2]/div[last()]').text

            # Shorten position
            if 'Fulfillment Center' in position:
                position = 'FC'
            elif 'Delivery Station' in position:
                position = 'DS'
            elif 'Distribution Center' in position:
                position = 'DC'
            elif 'XL' in position:
                position = 'XL'
            else:
                position = '??'

            if match := RE_LOCATION.match(location):
                job = JobItem(
                    position,
                    match.group('city'),
                    match.group('state')
                )
            else:
                job = JobItem(
                    position,
                    'Unknown',
                    '??'
                )

            jobs.append(job)

        wb.jitter(3, 5)

    if not jobs:
        exit()

    content = ''
    for j in jobs:
        content += f"✅ {j.position} @ {j.city}, {j.state}\n"

    with Pushover(CFG['pushover']['api_key'], CFG['pushover']['user_key']) as p:
        p.message(content)
