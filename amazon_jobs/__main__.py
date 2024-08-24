import re
from datetime import timedelta
from string import Template
from selenium.common.exceptions import NoSuchElementException

from . import logger
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
        case 'Sortation Center Warehouse Associate':
            code = 'SC'
        case 'Distribution Center Associate':
            code = 'DC'
        case 'Locker+ Customer Service Associate':
            code = 'L+'
        case 'XL Warehouse Associate':
            code = 'XL'
        case 'Grocery Warehouse Associate':
            code = 'GW'
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
                logger.error((
                    'Could not locate job description web elements!\n\n'
                    f'HTML:\n{item.get_attribute("outerHTML")}'
                ))
                continue

            try:
                position = parse_job_position(position_text)
                location = parse_job_location(location_text)
            except ValueError:
                logger.error((
                    'Could not parse job information from text!\n\n'
                    f'Position:\n{position_text}\n\n'
                    f'Location:\n{location_text}'
                ))
                continue

            job_item = JobItem(position, location)

            if not job_item_cached(job_item, timedelta(hours=1)):
                insert_job_item(job_item)
                jobs.append(job_item)
            else:
                logger.info((
                    f'{job_item.position.code} @ '
                    f'{job_item.location.city}, '
                    f'{job_item.location.state} '
                    'is cached, skipping...'
                ))

        wb.jitter(3, 5)

    if not jobs:
        exit()

    content = ''
    for j in jobs:
        content += (
            f'✅ {j.position.code} @ '
            f'{j.location.city}, '
            f'{j.location.state}\n'
        )

    with Pushover(CFG['pushover']['api_key'], CFG['pushover']['user_key']) as p:
        p.message(content)
