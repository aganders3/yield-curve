from indicator import data

import datetime

DATABASE = 'indicator.db'

if __name__ == "__main__":
    # oldest yield curve data is 1990-01-02
    d = datetime.date(1990, 1, 2)
    one_day = datetime.timedelta(1)

    while d != datetime.date.today():
        print(data._get_yield_rates(d))
        d += one_day
