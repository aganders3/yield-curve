from indicator import app, data

from flask import jsonify, redirect, render_template, request

import datetime

@app.route('/')
@app.route('/<int:yyyy>-<int:mm>-<int:dd>')
def index(yyyy=None, mm=None, dd=None):
    try:
        date = datetime.date(yyyy, mm, dd)
    except (TypeError, ValueError, OverflowError):
        today = datetime.date.today()
        date = today

    one_day = datetime.timedelta(1)

    yield_rates, _ = data.get_yield_rates(date)
    while yield_rates is None:
        date -= one_day
        yield_rates, _ = data.get_yield_rates(date)

    if yield_rates is not None:
        rates_only = [yield_rates['m1'], yield_rates['m3'], yield_rates['m6'],
                      yield_rates['y1'], yield_rates['y2'], yield_rates['y3'],
                      yield_rates['y5'], yield_rates['y7'], yield_rates['y10'],
                      yield_rates['y20'], yield_rates['y30']]
    else:
        rates_only = []

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
