from indicator import data, models, db

import argparse
import datetime
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crawl treasury.gov for data.')

    parser.add_argument('-q', '--quiet')

    args = parser.parse_args()

    # oldest yield curve data is 1990-01-02
    # d = datetime.date(2018, 8, 1)
    d = datetime.date(1990, 1, 2)
    one_day = datetime.timedelta(1)

    while d != datetime.date.today():
        rates = data.get_yield_rates(d)
        if args.q is not None:
            print(rates)
        if rates is not None:
            y = models.YieldRates(**rates)
            db.session.add(y)
        d += one_day
    db.session.commit()
