from indicator import models

import requests
import datetime
import xml.etree.ElementTree as ET

XML_NS = '{http://schemas.microsoft.com/ado/2007/08/dataservices}'

DTAGS = ['BC_1MONTH', 'BC_3MONTH', 'BC_6MONTH', 'BC_1YEAR', 'BC_2YEAR',
        'BC_3YEAR', 'BC_5YEAR', 'BC_7YEAR', 'BC_10YEAR', 'BC_20YEAR',
        'BC_30YEAR']
TIMES = ['m1', 'm3', 'm6', 'y1', 'y2', 'y3', 'y5', 'y7', 'y10', 'y20', 'y30']

DTAGS_DICT = {(XML_NS + dtag) : time for dtag, time in zip(DTAGS, TIMES)}

def get_yield_rates(date=None, strict=False):
    """Get the yield rates
    first try to pull from the DB, but fall back on scraping treasury.gov"""

    if date is None:
        all_yield_rates = models.YieldRates.query.all()
        return [y.as_dict() for y in all_yield_rates], True

    if strict:
        window = 0 # don't search nearby dates
    else:
        window = 15 # search within a window (window/2 days forward and back)

    # we know there is no data before 1990
    if date < datetime.date(1990, 1, 1):
        return None, False

    rates = None
    i = 0
    while rates is None and i <= window:
        # bounce back and forth moving away from "today" to find the nearest
        # date that works
        if i % 2 == 0:
            date = date + datetime.timedelta(i)
        else:
            date = date - datetime.timedelta(i)
        i += 1

        # first check the database
        rates_from_db = models.YieldRates.query.filter_by(date=date).first()
        in_db = True

        if rates_from_db is None:
            # try to look it up if it's not in the database yet
            in_db = False
            rates = _get_yield_rates(date)
        else:
            # otherwise just return the data
            rates = rates_from_db.as_dict()

    return rates, in_db

def _get_yield_rates(date):
    """Get the yield rates from treasury.gov"""

    request_filter = ('day(NEW_DATE) = {} and '
                      'month(NEW_DATE) = {} and '
                      'year(NEW_DATE) = {}')
    request_filter = request_filter.format(date.day, date.month, date.year)
    request_filter = request_filter.replace(' ', '%20')
    request_filter = request_filter.replace('=', 'eq')

    request_url = ('http://data.treasury.gov/feed.svc/'
                   'DailyTreasuryYieldCurveRateData?$filter=')

    response = requests.get(request_url + request_filter)

    root = ET.fromstring(response.text)

    entry = root.find("{http://www.w3.org/2005/Atom}entry")

    if entry is not None:
        content = entry.find("{http://www.w3.org/2005/Atom}content")

        data_xml = content[0]
        data = {'date': date}

        data_ = {}
        for d in data_xml:
            if d.tag in DTAGS_DICT:
                try:
                    rate = float(d.text)
                except TypeError:
                    rate = None
                data_[DTAGS_DICT[d.tag]] = rate

        data['data'] = [data_[t] for t in TIMES]
        data['label'] = data['date'].isoformat()
    else:
        data = None

    return data
