import calendar
import datetime

import pandas as pd
from matplotlib.ticker import FuncFormatter


def load_dates_with_second_duration_starting_some_year(time_values, year):
    start_date = datetime.datetime(year=year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    print(time_values)
    return start_date + pd.to_timedelta(time_values, unit='s')


def get_all_366_days():
    start_date = datetime.datetime(year=2008, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    return [start_date + datetime.timedelta(days=x) for x in range(366)]


def get_all_days_str():
    return [str(d).split()[0][5:] for d in get_all_366_days()]


def transform_index_as_dates(ax):
    formatter = FuncFormatter(lambda x_val, tick_pos: get_all_days_str()[int(x_val)])
    ax.xaxis.set_major_formatter(formatter)


def get_index_15th_of_the_month():
    return [i for i, s in enumerate(get_all_days_str()) if s.endswith('-15')]


def get_index_crossing_between_months():
    return [i - 0.5 for i, s in enumerate(get_all_days_str()[1:]) if s.endswith('-01')]


def get_daily_index(month: int):
    check_month_type(month)
    return [i for i, s in enumerate(get_all_days_str()) if s.startswith(f'{month:02d}-')]


def get_monthly_index(month: int):
    check_month_type(month)
    return [month - 1]


def check_month_type(month):
    assert isinstance(month, int)
    assert 1 <= month <= 12


def get_month_names() -> list[str]:
    """Return a copy of the list month_names"""
    return ['January', 'February', 'March', 'April', 'May', 'June', 'July',
            'August', 'September', 'October', 'November', 'December']


if __name__ == '__main__':
    print(get_all_days_str())
    print(len(get_all_days_str()))
    print(get_index_15th_of_the_month())
    print(get_index_crossing_between_months())
    print(get_daily_index(3))
