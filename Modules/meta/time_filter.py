import time

second = 1
minute = 60 * second
hour = 60*minute
day = 24*hour
week = 7*day
month = 30*day
year = 365*day

times = [
    {"name": "year", "value": year},
    {"name": "month", "value": month},
    {"name": "week", "value": week},
    {"name": "day", "value": day},
    {"name": "hour", "value": hour},
    {"name": "minute", "value": minute},
    {"name": "second", "value": second},
]


def get_ago(time_val):
    
    time_val = (time.time() - time_val)
    
    for i in times:
        val = time_val//i["value"]
        if val > 0:
            if val > 1:
                return str(val)+" "+i["name"]+"s ago"
            return str(val)+" "+i["name"]+" ago"
    
    return "0 seconds ago"