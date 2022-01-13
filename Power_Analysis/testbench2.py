import Power_Analysis.db_login as login
import Power_Analysis.db_search as search
import Power_Analysis.db_update as update
from datetime import datetime, timedelta
from calendar import monthrange

def mins_in_period(date_1, date_2):
    time_delta = (date_2 - date_1)
    total_seconds = time_delta.total_seconds()
    return round(total_seconds / 60)

def gen_date_list(max_d, min_d):
    #date_2 = datetime.strptime((min_d.strftime("%b-%d-%Y") + " 23:59:59"), "%b-%d-%Y %H:%M:%S")
    dates, mins = [], []
    print(mins_in_period(min_d, max_d))

    for i in range((max_d - min_d).days + 1):
        dates.append((min_d + timedelta(i)).strftime("%b-%d-%Y"))

        if i != (max_d - min_d).days:
            date_2 = datetime.strptime(((min_d + timedelta(i)).strftime("%b-%d-%Y") + " 23:59:59")
                                           , "%b-%d-%Y %H:%M:%S")
        else:
            date_2 = max_d

        min = mins_in_period(min_d, date_2)
        mins.append(min - sum(mins))

    return dates, mins

def divide_hours(begin, date, first_day = True):
    off1_begin = datetime.strptime((date + " 00:00:00"), "%b-%d-%Y %H:%M:%S")
    off1_end = datetime.strptime((date + " 06:59:59"), "%b-%d-%Y %H:%M:%S")
    off2_begin = datetime.strptime((date + " 19:00:00"), "%b-%d-%Y %H:%M:%S")
    #off2_end = datetime.strptime((date + " 23:59:59"), "%b-%d-%Y %H:%M:%S")
    mid_begin = datetime.strptime((date + " 11:00:00"), "%b-%d-%Y %H:%M:%S")
    mid_end = datetime.strptime((date + " 16:59:59"), "%b-%d-%Y %H:%M:%S")
    on1_begin = datetime.strptime((date + " 7:00:00"), "%b-%d-%Y %H:%M:%S")
    on1_end = datetime.strptime((date + " 10:59:59"), "%b-%d-%Y %H:%M:%S")
    on2_begin = datetime.strptime((date + " 17:00:00"), "%b-%d-%Y %H:%M:%S")
    on2_end = datetime.strptime((date + " 19:59:59"), "%b-%d-%Y %H:%M:%S")
    res = [0, 0, 0] # off_peak, mid_peak, on_peak

    if begin < off1_end:
        res[0] += mins_in_period(date_1 = off1_begin, date_2 = begin)
    elif begin < on1_end:
        res[0] += 7 * 60
        res[2] += mins_in_period(date_1 = on1_begin, date_2 = begin)
    elif begin < mid_end:
        res[0] += 7 * 60
        res[1] += mins_in_period(date_1 = mid_begin, date_2 = begin)
        res[2] += 4 * 60
    elif begin < on2_end:
        res[0] += 7 * 60
        res[1] += 6 * 60
        res[2] += 4 * 60 + mins_in_period(date_1 = on2_begin, date_2 = begin)
    else:
        res[0] += 7 * 60 + mins_in_period(date_1 = off2_begin, date_2 = begin)
        res[1] += 6 * 60
        res[2] += 6 * 60

    if first_day:
        res[0] = round(12 * 60 - res[0])
        res[1] = round(6 * 60 - res[1])
        res[2] = round(6 * 60 - res[2])
    return res

min_date = "Jan-12-2022 07:00:00"
max_date = "Jan-17-2022 07:00:00"

min_d = datetime.strptime(min_date, "%b-%d-%Y %H:%M:%S")
max_d = datetime.strptime(max_date, "%b-%d-%Y %H:%M:%S")
date_list, mins_list = gen_date_list(max_d,min_d)
print(date_list, mins_list)

pd = {}
power_calendar_divided = {}
for id, d in enumerate(date_list):
    if d in pd:
        pd[d] += 0.1 * mins_list[id]
    else:
        pd.update({d: 0.1 * mins_list[id]})

    # update the power usage by category each day
    date_time_d = datetime.strptime(d, "%b-%d-%Y")
    off_peak = 0
    if date_time_d.weekday() > 5:
        off_peak += 0.1 * mins_list[id]

        if d in power_calendar_divided:
            power_calendar_divided[d]["off_peak"] += 0.1 * mins_list[id]
        else:
            power_calendar_divided.update(
                {d: {"off_peak": 0.1 * mins_list[id], "on_peak": 0, "mid_peak": 0}})

    else:  # non-weekend
        if mins_list[id] == 24 * 60:  # whole day
            if d in power_calendar_divided:
                power_calendar_divided[d]["off_peak"] += round(0.1 * 12 * 60)
                power_calendar_divided[d]["on_peak"] += round(0.1 * 6 * 60)
                power_calendar_divided[d]["mid_peak"] += round(0.1 * 6 * 60)
            else:
                power_calendar_divided.update(
                    {d: {"off_peak": round(0.1 * 12 * 60), "on_peak": round(0.1 * 6 * 60), "mid_peak": round(0.1 * 6 * 60)}})
        else:
            if id == 0:
                begin = min_d
                prefix = begin.strftime("%b-%d-%Y")
                division = divide_hours(begin=begin, date=prefix, first_day=True)
            else:
                begin = max_d
                prefix = begin.strftime("%b-%d-%Y")
                division = divide_hours(begin=begin, date=prefix, first_day=False)

            if d in power_calendar_divided:
                power_calendar_divided[d]["off_peak"] += round(division[0] * 0.1)
                power_calendar_divided[d]["on_peak"] += division[2] * 0.1
                power_calendar_divided[d]["mid_peak"] += division[1] * 0.1
            else:
                power_calendar_divided.update(
                    {d: {"off_peak": division[0] * 0.1, "on_peak": division[2] * 0.1, "mid_peak": division[1] * 0.1}})
print(pd)
print(power_calendar_divided)

# month = datetime.now().strftime("%b")
# num_days = monthrange(int(datetime.now().strftime("%Y"))
#                           , int(datetime.now().strftime("%m")))[1]
#
# min_date = month + '-01' + datetime.now().strftime("-%Y") + " 23:58:59"
# max_date = month + '-' + str(num_days) + datetime.now().strftime("-%Y") + " 04:59:59"
#
# min_d = datetime.strptime(min_date, "%b-%d-%Y %H:%M:%S")
# max_d = datetime.strptime(max_date, "%b-%d-%Y %H:%M:%S")
#
#
# diff = max_d - min_d
# for i in range(diff.days + 1):
#     print((min_d + timedelta(i)).strftime("%b-%d-%Y"))
#     print (min_d + timedelta(i))


#print(int(datetime.now().strftime("%Y")))