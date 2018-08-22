from indicator import app

from flask import jsonify, redirect, render_template, request

import requests

import datetime
import xml.etree.ElementTree as ET

DTAGS = ('{http://schemas.microsoft.com/ado/2007/08/dataservices}BC_1MONTH',
         '{http://schemas.microsoft.com/ado/2007/08/dataservices}BC_3MONTH',
         '{http://schemas.microsoft.com/ado/2007/08/dataservices}BC_6MONTH',
         '{http://schemas.microsoft.com/ado/2007/08/dataservices}BC_1YEAR',
         '{http://schemas.microsoft.com/ado/2007/08/dataservices}BC_2YEAR',
         '{http://schemas.microsoft.com/ado/2007/08/dataservices}BC_3YEAR',
         '{http://schemas.microsoft.com/ado/2007/08/dataservices}BC_5YEAR',
         '{http://schemas.microsoft.com/ado/2007/08/dataservices}BC_7YEAR',
         '{http://schemas.microsoft.com/ado/2007/08/dataservices}BC_10YEAR',
         '{http://schemas.microsoft.com/ado/2007/08/dataservices}BC_20YEAR',
         '{http://schemas.microsoft.com/ado/2007/08/dataservices}BC_30YEAR')

@app.route('/')
def index():
    yesterday = datetime.date.today() - datetime.timedelta(1)
    data = get_data(yesterday)

    return render_template('base.html',
                           date=yesterday.isoformat(),
                           data=data)

def get_data(date=None):
    if date is None:
        yesterday = datetime.date.today() - datetime.timedelta(1)
        date = yesterday

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
    content = entry.find("{http://www.w3.org/2005/Atom}content")

    data_xml = content[0]
    data = []
    for d in data_xml:
        if d.tag in DTAGS:
            data.append(float(d.text))

    return data

# @app.route('/<int:seed>')
# def occupation(seed):
#     ima, fantasy_occupation = generate_occupation(seed)
#
#     return render_template('base.html',
#                            fantasy_occupation=fantasy_occupation,
#                            ima=ima,
#                            seed=seed)

# @app.route('/json')
# def json():
#     if 'seed' in request.args.keys():
#         seed = request.args.get('seed')
#     else:
#         seed = random.randint(0, 999999999)
#
#     ima, fantasy_occupation = generate_occupation(seed)
#
#     return jsonify({'success': True,
#                         'data' : {
#                             'job_string' : fantasy_occupation,
#                             'ima' : ima,
#                             'seed' : seed
#                             }
#                    }
#                   )
