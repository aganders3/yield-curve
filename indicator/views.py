from indicator import app, data

from flask import jsonify, redirect, render_template, request

import datetime
from dateutil.relativedelta import relativedelta

# TODO: do this without dateutil, maybe?
DEFAULT_DELTAS = [('Today', relativedelta(0)),
                  ('Last Month', relativedelta(months=-1)),
                  ('Three Months Ago', relativedelta(months=-3)),
                  ('Six Months Ago', relativedelta(months=-6)),
                  ('Last Year', relativedelta(years=-1)),
                  ('Two Years Ago', relativedelta(years=-2)),
                  ('Three Years Ago', relativedelta(years=-3)),
                  ('Five Years Ago', relativedelta(years=-5))]
#                   relativedelta(years=-7),
#                   relativedelta(years=-10)]

@app.route('/')
@app.route('/<date_str>')
def index(date_str=None):
    today = datetime.date.today()
    # parse the date from the query string if present (use today if not)
    if date_str is None:
        date_str = request.args.get('date',
                                    default=today.isoformat())
    try:
        yyyy, mm, dd = map(int, date_str.split('-'))
        date = datetime.date(yyyy, mm, dd)
    except (TypeError, ValueError, OverflowError):
        date = today

    yield_rates = []
    for delta in DEFAULT_DELTAS:
        y, _ = data.get_yield_rates(date + delta[1])
        if y is None:
            continue

        if date != today and delta[1] == relativedelta(0):
            y['label'] = y['date'].isoformat()
        else:
            y['label'] = delta[0]

        yield_rates.append(y)

    # TODO: add TODAY no matter what?

    if request.args.get('json'):
        return jsonify(data=yield_rates)
    else:
        return render_template('base.html',
                               data=yield_rates)

# @login_required
@app.route('/yields/', methods=['GET', 'POST'])
def _yields():
    if request.method == 'GET':
        y, _ = data.get_yield_rates()

        return jsonify(y)

    if request.method == 'POST':
        # TODO - add the record for the date to the DB
        return jsonify(None), 401

@app.route('/yields/<date_str>', methods=['GET', 'PUT'])
def _yield(date_str):
    try:
        yyyy, mm, dd = map(int, date_str.split('-'))
        date = datetime.date(yyyy, mm, dd)
    except (TypeError, ValueError, OverflowError):
        date = None

    if request.method == 'GET':
        if date is not None:
            y, _ = data.get_yield_rates(date)
        else:
            y = None

        return jsonify(y)

    if request.method == 'PUT':
        # TODO - modify the existing record
        return jsonify(None), 401
