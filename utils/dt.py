import datetime

def now_tz_offset(offset):
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=offset))).replace(microsecond=0).isoformat()

def humanize_date(date_str):
    return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%d.%m.%Y")