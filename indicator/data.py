from indicator import models

import requests
import datetime
import xml.etree.ElementTree as ET

XML_NS = '{http://schemas.microsoft.com/ado/2007/08/dataservices}'

DTAGS = {(XML_NS + 'BC_1MONTH') : 'm1',
         (XML_NS + 'BC_3MONTH') : 'm3',
         (XML_NS + 'BC_6MONTH') : 'm6',
         (XML_NS + 'BC_1YEAR')  : 'y1',
         (XML_NS + 'BC_2YEAR')  : 'y2',
         (XML_NS + 'BC_3YEAR')  : 'y3',
         (XML_NS + 'BC_5YEAR')  : 'y5',
         (XML_NS + 'BC_7YEAR')  : 'y7',
         (XML_NS + 'BC_10YEAR') : 'y10',
         (XML_NS + 'BC_20YEAR') : 'y20',
         (XML_NS + 'BC_30YEAR') : 'y30'}

def get_yield_rates(date=None):
    if date is None:
        return models.YieldRates.query.all(), True

    # first check the database
    rates_from_db = models.YieldRates.query.filter_by(date=date).first()
    in_db = True

    # try to look it up if it's not in the database yet
    if rates_from_db is None:
        in_db = False
        rates = _get_yield_rates(date)
    else:
        rates = rates_from_db._values_as_dict()

    return rates, in_db

def _get_yield_rates(date):
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
        for d in data_xml:
            if d.tag in DTAGS:
                try:
                    rate = float(d.text)
                except TypeError:
                    rate = None
                data[DTAGS[d.tag]] = rate
    else:
        data = None

    return data
