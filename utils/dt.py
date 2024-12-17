import datetime

def now_tz_offset(offset):
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=offset))).replace(microsecond=0).isoformat()