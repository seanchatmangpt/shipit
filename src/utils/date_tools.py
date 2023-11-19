import datetime


def next_friday() -> str:
    today = datetime.date.today()
    friday = today + datetime.timedelta((4 - today.weekday()) % 7)
    # convert to YYYY-MM-DD format
    return friday.strftime("%Y-%m-%d")
