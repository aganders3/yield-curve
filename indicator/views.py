from indicator import app, data

from flask import jsonify, redirect, render_template, request

import datetime

@app.route('/')
def index():
    today = datetime.date.today()
    # parse the date from the query string if present (use today if not)
    date_str = request.args.get('date',
                                default=today.isoformat())
    try:
        yyyy, mm, dd = map(int, date_str.split('-'))
        date = datetime.date(yyyy, mm, dd)
    except (TypeError, ValueError, OverflowError):
        date = today

    # walk backwards one day at a time to find the closest data
    # but don't go back farther than a week
    one_day = datetime.timedelta(1)
    for i in range(7):
        yield_rates, _ = data.get_yield_rates(date)
        if yield_rates is not None:
            break
        else:
            date -= one_day

    # TODO: move this to a function
    if yield_rates is not None:
        rates_only = [yield_rates['m1'], yield_rates['m3'], yield_rates['m6'],
                      yield_rates['y1'], yield_rates['y2'], yield_rates['y3'],
                      yield_rates['y5'], yield_rates['y7'], yield_rates['y10'],
                      yield_rates['y20'], yield_rates['y30']]
    else:
        date += datetime.timedelta(7)
        rates_only = []

    if request.args.get('json'):
        return jsonify(date=date.isoformat(), data=rates_only)
    else:
        return render_template('base.html',
                               date=date.isoformat(),
                               data=rates_only)

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
