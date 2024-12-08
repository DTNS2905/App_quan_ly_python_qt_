import datetime

import pytz


def convert_utc_time_to_timezone(timestamp_utc, zone="Asia/Bangkok"):
    timezone = pytz.timezone(zone)
    return (
        datetime.datetime.fromisoformat(timestamp_utc)
        .replace(tzinfo=pytz.utc)
        .astimezone(timezone)
    )
