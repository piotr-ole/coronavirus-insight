import math

def calc_log(value, base = 10, rounds=True):
    if value == 0:
        return 0
    log = math.log(value, base)
    if rounds:
        return int(round(log, 0))
    return log