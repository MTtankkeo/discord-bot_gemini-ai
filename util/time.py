from datetime import datetime

# Returns the datetime object converted to string format.
def to_string_by_time(time: datetime):
    return time.strftime('%Y-%m-%d %H:%M:%S')