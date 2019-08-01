#!/usr/bin/env python
"""
Syntax: view.py [-w <who>] [all | week | fortnight | month | quarter | stats | <n>]
     (default is month)
"""
#    Copyright (C) 2006--2009 Dave Gabrielson <dave -AT- gabrielson -DOT- ca>
#    This program can be distributed under the terms of the GNU GPL.
#    See the file COPYING.

import exceptions
import getopt
# Setup Django environment
import os
import sys
import tempfile
import time

from diet.models import Person, WeightEntry

sys.path.insert(0, os.path.expanduser('~/django'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'





gnuplot_cmd = '''
# set datafile separator ","    # for CSV files
set xdata time
set timefmt "%%Y-%%m-%%d"  # The dates in the file look like 2004-07-25
set format x "%%b %%d"     # On the x-axis, we want tics like Jul 25
set bars small             # don't show error bars
set xrange ["%s":"%s"]     # show just enough. No more.
plot \
    '%s' using 1:3 with lines title 'Trend', \
    '%s' using 1:2:4:5 with yerrorbars pt 4 title 'Weight'
'''


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




def load(who):
    p = Person.objects.get(name__iexact=who)
    db_data = WeightEntry.objects.filter(who=p).order_by('date')
    
    return [ [str(entry.date), str(entry.weight), str(entry.trend), str(min([entry.weight, entry.trend])), str(max([entry.weight, entry.trend]))] for entry in db_data ]



def view(who, how_much):

    data = load(who)
    days = days_to_integers( [record[0] for record in data] )
    trend = [ float(record[2]) for record in data ]
    N = days[-1] - days[0]


    if how_much <= 0:
        if how_much < 0:
            X, Y = last_n_days(days, trend, -how_much)
            how_much = -len(X)

        show_data = data[how_much:]

        print '+--------+--------+-------+------+'
        print '|  Date  | Weight | Trend |  Net |'
        print '+--------+--------+-------+------+'
        old_trnd = 0.0
        for record in show_data:
            print time.strftime('| %b %d |', time.strptime(record[0], '%Y-%m-%d')),
            weight, trnd = [ float(item) for item in record[1:3] ]
            print ' %.1f |' % weight,
            print '%.1f |' % trnd,
            if 1: #old_trend != 0.0:
                net = weight-trnd
                print '% .1f |' % net,
            #else:
            #    print '     |',
            old_trnd = trnd
            print
        print '+--------+--------+-------+------+'


    print
    print 'Statistics  [lbs/week]   [kcals/day]'
    print

    if N >= 7:
        X, Y = last_n_days(days, trend, 7)
        m = least_squares_slope( X, Y )
        print '       week:', round(m*70)/10.0, '\t ', int(round(m*3500))

    if N >= 14:
        X, Y = last_n_days(days, trend, 14)
        m = least_squares_slope( X, Y )
        print '  fortnight:', round(m*70)/10.0, '\t ', int(round(m*3500))

    if N >= 30:
        X, Y = last_n_days(days, trend, 30)
        m = least_squares_slope( X, Y )
        print '      month:', round(m*70)/10.0, '\t ', int(round(m*3500))

    if N >= 90:
        X, Y = last_n_days(days, trend, 90)
        m = least_squares_slope( X, Y )
        print '    quarter:', round(m*70)/10.0, '\t ', int(round(m*3500))

    if N >= 180:
        X, Y = last_n_days(days, trend, 180)
        m = least_squares_slope( X, Y )
        print '  half-year:', round(m*70)/10.0, '\t ', int(round(m*3500))

    if N >= 365:
        X, Y = last_n_days(days, trend, 365)
        m = least_squares_slope( X, Y )
        print '       year:', round(m*70)/10.0, '\t ', int(round(m*3500))

    #m = least_squares_slope( days, trend )
    #print '%6.d days:' % days[-1], round(m*70)/10.0, '\t ', int(round(m*3500))

    print

    if how_much <= 0:
        tmp = tempfile.NamedTemporaryFile()
        print >> tmp, '\n'.join( [ ' '.join(line) for line in show_data] )
        tmp.flush()

        days = [ time.mktime(time.strptime(record[0], '%Y-%m-%d')) for record in show_data ]
        start = min(days) - 60*60*24
        stop = max(days) + 60*60*24

        start_s = time.strftime('%Y-%m-%d', time.localtime(start))
        stop_s = time.strftime('%Y-%m-%d', time.localtime(stop))

        pipe = os.popen('gnuplot 2>/dev/null', 'wt')
        pipe.write(gnuplot_cmd % (start_s, stop_s, tmp.name, tmp.name))
        pipe.flush()

        raw_input("Press ENTER to continue... ")



def main(user, args):
    try:
        opts, noopts = getopt.getopt(args, "w:")
    except getopt.GetoptError:
        return __doc__

    who = user

    for opt, arg in opts:
        if opt == '-w':
            who = arg
        elif opt == '-?':
            return __doc__
        else:
            return __doc__ + "\n\n(Invalid option.)"

    if len(noopts) > 1:
        return __doc__ + "\n\n(You specified more than one [non-option] argument.)"

    #if len(args) not in [1, 2]:
        #print __doc__
        #return

    who = who.lower()

    if len(noopts) == 0:
        how_much = -30
    else:
        if noopts[0] == 'all':
            how_much = 0
        elif noopts[0] == 'year':
            how_much = -365
        elif noopts[0] == 'halfyear':
            how_much = -180
        elif noopts[0] == 'quarter':
            how_much = -90
        elif noopts[0] == 'month':
            how_much = -30
        elif noopts[0] == 'fortnight':
            how_much = -14
        elif noopts[0] == 'week':
            how_much = -7
        elif noopts[0] == 'stats':
            how_much = +1   # note positive value
        else:
            try:
                how_much = int(noopts[0])
                if how_much < 0:
                    return __doc__
                how_much *= -1
            except ValueError:
                return __doc__

    view(who, how_much)



if __name__ == '__main__':
    import sys,os
    v = main(os.environ['USER'], sys.argv[1:])
    if v:
        print v
