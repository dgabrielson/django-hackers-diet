#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Syntax: forecast.py [-w <who>] <goal>

"""
#    Copyright (C) 2007--2009 Dave Gabrielson <dave -AT- gabrielson -DOT- ca>
#    This program can be distributed under the terms of the GNU GPL.
#    See the file COPYING.

import exceptions
import getopt
# Setup Django environment
import os
import sys
import tempfile
import time

import common

sys.path.insert(0, os.path.expanduser('~/django'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'




def least_squares_slope(X1, X2=None):
    if X2 == None:
        n = len(X1)
        X = [i+1 for i in range(n)]
        Y = X1
    else:
        X = X1
        Y = X2
        n = len(X)
        if len(Y) != n:
            raise exceptions.IndexError('List sizes for least_square_slope() must match!')

    XY = map(lambda x, y: x*y, X, Y)
    sumXY = sum(XY)
    sumX = sum(X)
    sumY = sum(Y)
    X2 = map(lambda x, y: x*y, X, X)
    sumX2 = sum(X2)

    return (n*sumXY - sumX*sumY)/(n*sumX2 - sumX**2)



def days_since_epoch(timestr):
    tt = time.strptime(timestr, '%Y-%m-%d')
    t = time.mktime(tt)
    return ( int(t) / (60*60*24) )



def days_to_integers(D):
    '''days_to_integers(D) -> <list of integers>

    Convert days to integers.
    Assume the 0th element of D maps to 1, and count up.
    '''
    baseline = days_since_epoch(D[0]) - 1
    I = []
    for d in D:
        i = days_since_epoch(d)
        I.append(i - baseline)

    return I



def last_n_days(D, R, n):
    base = D[-1] - n + 1
    i = -1
    while D[i] > base:
        i -= 1
    return D[i:], R[i:]



def view_merge(raw, calc):
    keys = raw.keys()
    keys.sort()
    return [ [k, str(raw[k]), str(calc[k]), str(min([raw[k], calc[k]])), str(max([raw[k], calc[k]])) ] for k in keys ]



def forecast(who, goal):
    result = ""
    raw = common.read_raw(who)
    calc = common.read_calc(who)

    data = view_merge(raw,calc) # a list
    days = days_to_integers( [record[0] for record in data] )
    trend = [ float(record[2]) for record in data ]
    N = days[-1] - days[0]

    delta_y = trend[-1] - goal
    now = time.time()

    result += '\n'
    result += 'Forecast    [lbs/week]  [date for goal]\n'
    result += '\n'

    forcast_time = lambda m : time.localtime(now - (24*60*60*delta_y/m))
    time_fmt = '%B %d, %Y'

    if N >= 7:
        X, Y = last_n_days(days, trend, 7)
        m = least_squares_slope( X, Y )
        result += '       week: ' + str(round(m*70)/10.0) + ' \t ' + time.strftime(time_fmt, forcast_time(m)) + '\n'

    if N >= 14:
        X, Y = last_n_days(days, trend, 14)
        m = least_squares_slope( X, Y )
        result += '  fortnight: ' + str(round(m*70)/10.0) + ' \t ' + time.strftime(time_fmt, forcast_time(m)) + '\n'

    if N >= 30:
        X, Y = last_n_days(days, trend, 30)
        m = least_squares_slope( X, Y )
        result += '      month: ' + str(round(m*70)/10.0) + ' \t ' + time.strftime(time_fmt, forcast_time(m)) + '\n'

    if N >= 90:
        X, Y = last_n_days(days, trend, 90)
        m = least_squares_slope( X, Y )
        result += '    quarter: ' + str(round(m*70)/10.0) + ' \t ' + time.strftime(time_fmt, forcast_time(m)) + '\n'

    if N >= 180:
        X, Y = last_n_days(days, trend, 180)
        m = least_squares_slope( X, Y )
        result += '  half-year: ' + str(round(m*70)/10.0) + ' \t ' + time.strftime(time_fmt, forcast_time(m)) + '\n'

    if N >= 365:
        X, Y = last_n_days(days, trend, 365)
        m = least_squares_slope( X, Y )
        result += '       year: ' + str(round(m*70)/10.0) + ' \t ' + time.strftime(time_fmt, forcast_time(m)) + '\n'

    result += '\n'
    return result



def main(user, args):
    try:
        opts, noopts = getopt.getopt(args, "w:")
    except getopt.GetoptError:
        return __doc__

    who = user

    for opt, arg in opts:
        if opt == '-w':
            who = arg
        else:
            return __doc__ + "\n\n(Invalid option.)"

    if len(noopts) > 1:
        return __doc__ + "\n\n(You specified more than one [non-option] argument.)"

    who = who.lower()

    if len(noopts) == 0:
        return __doc__ + "\n\n(You must supply a goal weight for forecasting.)"
    else:
        try:
            goal = float(noopts[0])
            if goal < 0:
                return __doc__ + "\n\n(The goal weight must be a positive number.)"
        except ValueError:
            return __doc__ + "\n\n(The goal weight must be a number.)"

    return forecast(who, goal)


if __name__ == '__main__':
    import sys,os
    print main(os.environ['USER'], sys.argv[1:])
