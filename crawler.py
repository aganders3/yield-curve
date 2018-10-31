from indicator import data, models, db

import argparse
import datetime
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crawl treasury.gov for data.')

    parser.add_argument('-d', '--date')
    parser.add_argument('--start-date')
    parser.add_argument('--end-date')
    parser.add_argument('-q', '--quiet', action = 'store_true')

    args = parser.parse_args()

    if args.date is None:
        # oldest yield curve data is 1990-01-02
        start_date = datetime.date(1990, 1, 2)
        if args.start_date is not None:
            yyyy, mm, dd = map(int, args.start_date.split('-'))
            start_date = datetime.date(yyyy, mm, dd)

        end_date = datetime.date.today()
        if args.end_date is not None:
            yyyy, mm, dd = map(int, args.end_date.split('-'))
            end_date  = datetime.date(yyyy, mm, dd)

        if not args.quiet:
            print("Fetching data from [{}, {}]...".format(start_date.isoformat(), end_date.isoformat()))
    else:
        # get a single date
        yyyy, mm, dd = map(int, args.date.split('-'))
        start_date = end_date = datetime.date(yyyy, mm, dd)
        if not args.quiet:
            print("Fetching data from [{}, {}]...".format(start_date.isoformat(), end_date.isoformat()))

    one_day = datetime.timedelta(1)

    d = start_date
    while d != (end_date + one_day):
        if d.weekday() == 5:
            d += (one_day + one_day)
            db.session.commit()
            continue

        rates, in_db = data.get_yield_rates(d, strict=True)
        if not args.quiet:
            print(d, rates)
        if rates is not None and not in_db:
            rates_dict['date'] = rates['date']
            rates_dict = {tag : rate for tag, rate in zip(data.TIMES, rates['data'])}
            y = models.YieldRates(**rates_dict)
            db.session.add(y)
        d += one_day

    db.session.commit()
