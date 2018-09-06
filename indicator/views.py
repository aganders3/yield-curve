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
