from datetime import timedelta
import re
from string import Template
from selenium.common.exceptions import NoSuchElementException
from . import AMAZON_JOBS_CONFIG as CFG
from .database import insert_job_item, job_item_cached
from .structures import JobItem, JobLocation, JobPosition
from ..alert import Pushover
from ..browser import Browser

AMAZON_JOBS_URL = Template(
    'https://hiring.amazon.com/app#/jobSearch?'
    'postal=$postal'
    '&locale=en-US'
)

def parse_job_position(text: str) -> JobPosition:
    pattern = (
        r'^(?P<name>[^\n]+)'
        r'(?:\n(?P<shifts>[0-9]+) shifts? available)?'
    )
    match = re.match(pattern, text)

    if not match:
        raise ValueError('Could not parse job position')

    name = match.group('name')

    match name:
        case 'Fulfillment Center Warehouse Associate':
            code = 'FC'
        case 'Delivery Station Warehouse Associate':
            code = 'DS'
        case 'Delivery Center Associate':
            code = 'DC'
        case 'Locker+ Customer Service Associate':
            code = 'L+'
        case _:
            code = '??'

    return JobPosition(name, int(match.group('shifts') or 0), code)
    
def parse_job_location(text: str) -> JobLocation:
    pattern = (
        r'(?:Within (?P<distance>[0-9\.]+) mi \|)?\s?'
        r'(?P<city>[^,\|]+), (?P<state>[A-Z]{2})'
    )
    match = re.match(pattern, text)

    if not match:
        raise ValueError('Could not parse job location')
    
    return JobLocation(
        match.group('city'),
        match.group('state'),
        float(match.group('distance') or 0.0)
    )

jobs = []

with Browser() as wb:
    for zip in CFG['amazon'].get('zips', []):
        wb.get(AMAZON_JOBS_URL.substitute(postal=zip))

        wb.jitter(3, 5)

        wb.clear_form_by_css('[data-test-id="consentBtn"]') # cookies
        wb.clear_form_by_css('[data-test-id="sortCloseModal"]') # notifications

        wb.jitter(3, 5)

        for item in wb.find_elements_by_class('jobCardItem'):
            try:
                position_text = wb.find_child_by_xpath(item, './div/div/div[2]/div[1]').text
                location_text = wb.find_child_by_xpath(item, './div/div/div[2]/div[last()]').text
            except NoSuchElementException:
                print('Error locating web elements')
                continue
            
            try:
                position = parse_job_position(position_text)
                location = parse_job_location(location_text)
            except ValueError:
                print('Error parsing text data')
                continue

            job = JobItem(position, location)

            # We cache
            if not job_item_cached(job): # else log?
                insert_job_item(job)
                jobs.append(job)

        wb.jitter(3, 5)

    if not jobs:
        exit()

    content = ''
    for j in jobs:
        content += f"✅ {j.position.code} @ {j.location.city}, {j.location.state}\n"

    with Pushover(CFG['pushover']['api_key'], CFG['pushover']['user_key']) as p:
        p.message(content)
