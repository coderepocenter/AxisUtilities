from datetime import datetime
_today_datetime = datetime.now()
__version__ = f"{_today_datetime.year % 100}." \
              f"{_today_datetime.month}." \
              f"{_today_datetime.day}." \
              f"{_today_datetime.hour * 3600 + _today_datetime.minute * 60 + _today_datetime.second}"
del _today_datetime