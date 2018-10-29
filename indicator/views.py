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
        y_ = {}
        y_['data'] = ['{:.2f}'.format(y[t]) for t in data.TIMES]
        # y_['date'] = y['date'].isoformat()
        y_['date'] = y['date'].strftime("%A, %B %d, %Y")
        y_['label'] = delta[0]
        yield_rates.append(y_)

    # TODO: add TODAY no matter what?

    if request.args.get('json'):
        return jsonify(data=yield_rates)
    else:
        return render_template('base.html',
                               data=yield_rates)

# @login_required
@app.route('/yields/', methods=['GET', 'POST'])
def yields():
    if request.method == 'GET':
        yield_rates, _ = data.get_yield_rates()

        return jsonify(list(map(lambda x: {'date' : x.date.isoformat(),
                                           'data' : [x.m1, x.m3, x.m6,
                                                     x.y1, x.y2, x.y3,
                                                     x.y5, x.y7, x.y10,
                                                     x.y20, x.y30]},
                                yield_rates)))

    if request.method == 'POST':
        # TODO - add the record for the date to the DB
        return jsonify(None), 401

@app.route('/yields/<date_str>', methods=['GET', 'PUT'])
def yield_(date_str):
    try:
        yyyy, mm, dd = map(int, date_str.split('-'))
        date = datetime.date(yyyy, mm, dd)
    except (TypeError, ValueError, OverflowError):
        date = None

    if request.method == 'GET':
        yield_rates, _ = data.get_yield_rates(date)

        if date is not None and yield_rates is not None:
            rates_only = [yield_rates['m1'], yield_rates['m3'], yield_rates['m6'],
                          yield_rates['y1'], yield_rates['y2'], yield_rates['y3'],
                          yield_rates['y5'], yield_rates['y7'], yield_rates['y10'],
                          yield_rates['y20'], yield_rates['y30']]

            return jsonify(date=date.isoformat(), data=rates_only)
        else:
            return jsonify(date=None, data=[])

    if request.method == 'PUT':
        # TODO - modify the existing record
        return jsonify(None), 401
