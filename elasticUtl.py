# def datetimeReader():

import numpy as np
from datetime import datetime

def datetimeReader(timeStr):
# timeStr = '2017-09-06T11:06:28.468035'
    year = int(timeStr.split('-')[0])
    month = int(timeStr.split('-')[1])
    day = int(timeStr.split('-')[2].split('T')[0])
    hour = int(timeStr.split('-')[2].split('T')[1].split(':')[0])
    minute = int(timeStr.split('-')[2].split('T')[1].split(':')[1])
    second = int(timeStr.split('-')[2].split('T')[1].split(':')[2].split('.')[0])
    microsecond = int(timeStr.split('-')[2].split('T')[1].split(':')[2].split('.')[1])
    return datetime(year, month, day, hour, minute, second, microsecond) 









