#!/usr/bin/env python

import sys
import time

import gnuplot_data

from diet.models import Person, WeightEntry

from . import bmi


# NOTE the *massive* pre-expansion of percent-signs.
# This string gets % evaluated **twice** and requires single percents
#   in the result.
gnuplot_pre = '''
# set datafile separator ","    # for CSV files
set xdata time
set timefmt "%%%%Y-%%%%m-%%%%d"  # The dates in the file look like 2004-07-25
set format x "%%%%b %%%%d"     # On the x-axis, we want tics like Jul 25
set bars small             # don't show error bars
set xrange ["%s":"%s"]     # show just enough. No more.
'''
gnuplot_plot = '''
plot \
    '%(datafile)s' using 1:3 with lines title 'Trend', \
    '%(datafile)s' using 1:2:4:5 with yerrorbars pt 4 title 'Weight'
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
            raise IndexError('List sizes for least_square_slope() must match!')

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
    if len(D) <= n:
        return D, R
    base = D[-1] - n + 1
    i = -1
    while D[i] > base:
        i -= 1
    return D[i:], R[i:]




def load(who):
    if isinstance(who, Person):
        p = who
    else:
        p = Person.objects.get(name__iexact=unicode(who))
    db_data = WeightEntry.objects.filter(who=p).order_by('date')
    
    return [ [str(entry.date), str(entry.weight), str(entry.trend), str(min([entry.weight, entry.trend])), str(max([entry.weight, entry.trend]))] for entry in db_data ]



def chart(who, how_much, display=False, width=320, height=280):

    assert not display, 'Displaying the chart is no longer supported'

    data = load(who)
    days = days_to_integers( [record[0] for record in data] )
    trend = [ float(record[2]) for record in data ]
    N = days[-1] - days[0]

    if how_much <= 0:
        if how_much < 0:
            X, Y = last_n_days(days, trend, -how_much)
            how_much = -len(X)

        show_data = data[how_much:]


    if how_much <= 0:

        days = [ time.mktime(time.strptime(record[0], '%Y-%m-%d')) for record in show_data ]
        start = min(days) - 60*60*24
        stop = max(days) + 60*60*24

        start_s = time.strftime('%Y-%m-%d', time.localtime(start))
        stop_s = time.strftime('%Y-%m-%d', time.localtime(stop))

        script = gnuplot_pre % (start_s, stop_s)
        script += gnuplot_plot
        #terminal = 'png transparent size %d,%d' % (width, height)
        terminal = 'png size %d,%d' % (width, height)
        img_data = gnuplot_data.Plot(data=show_data, script=script, 
                                     terminal=terminal).plot()
        return img_data

    assert False, 'somethings wrong'



def stats(who):

    data = load(who)
    days = days_to_integers( [record[0] for record in data] )
    trend = [ float(record[2]) for record in data ]
    N = days[-1] - days[0]

    results = {'lbs':{}, 'kcals':{}}
    if N >= 7:
        X, Y = last_n_days(days, trend, 7)
        m = least_squares_slope( X, Y )
        #print '       week:', round(m*70)/10.0, '\t ', int(round(m*3500))
        results['week'] = True
        results['lbs']['week'] = round(m*70)/10.0
        results['kcals']['week'] = int(round(m*3500))

    if N >= 14:
        X, Y = last_n_days(days, trend, 14)
        m = least_squares_slope( X, Y )
        #print '  fortnight:', round(m*70)/10.0, '\t ', int(round(m*3500))
        results['fortnight'] = True
        results['lbs']['fortnight'] = round(m*70)/10.0
        results['kcals']['fortnight'] = int(round(m*3500))

    if N >= 30:
        X, Y = last_n_days(days, trend, 30)
        m = least_squares_slope( X, Y )
        #print '      month:', round(m*70)/10.0, '\t ', int(round(m*3500))
        results['month'] = True
        results['lbs']['month'] = round(m*70)/10.0
        results['kcals']['month'] = int(round(m*3500))

    if N >= 90:
        X, Y = last_n_days(days, trend, 90)
        m = least_squares_slope( X, Y )
        #print '    quarter:', round(m*70)/10.0, '\t ', int(round(m*3500))
        results['quarter'] = True
        results['lbs']['quarter'] = round(m*70)/10.0
        results['kcals']['quarter'] = int(round(m*3500))

    if N >= 180:
        X, Y = last_n_days(days, trend, 180)
        m = least_squares_slope( X, Y )
        #print '  half-year:', round(m*70)/10.0, '\t ', int(round(m*3500))
        results['halfyear'] = True
        results['lbs']['halfyear'] = round(m*70)/10.0
        results['kcals']['halfyear'] = int(round(m*3500))

    if N >= 365:
        X, Y = last_n_days(days, trend, 365)
        m = least_squares_slope( X, Y )
        #print '       year:', round(m*70)/10.0, '\t ', int(round(m*3500))
        results['year'] = True
        results['lbs']['year'] = round(m*70)/10.0
        results['kcals']['year'] = int(round(m*3500))

    return results



def table(who, how_much):

    data = load(who)
    days = days_to_integers( [record[0] for record in data] )
    trend = [ float(record[2]) for record in data ]
    N = days[-1] - days[0]


    if how_much <= 0:
        if how_much < 0:
            X, Y = last_n_days(days, trend, -how_much)
            how_much = -len(X)

        show_data = data[how_much:]

        results = []
        #print '+--------+--------+-------+------+'
        #print '|  Date  | Weight | Trend |  Net |'
        #print '+--------+--------+-------+------+'
        old_trnd = 0.0
        for record in show_data:
            D = time.strftime('%b %d', time.strptime(record[0], '%Y-%m-%d'))
            weight, trnd = [ float(item) for item in record[1:3] ]
            W = ' %.1f' % weight
            T = '%.1f' % trnd
            net = weight-trnd
            N = '% .1f' % net
            old_trnd = trnd
            #print
            results.append( [D,W,T,N] )
        #print '+--------+--------+-------+------+'
        return results


def do_bmi(p, weight):
    feet, inches = p.stature.split('\'')
    height = int(feet)*12.0 + float(inches.strip('"'))
    bmi_f, desc = bmi.bmi_desc(float(weight), height)
    return bmi_f, desc


###########
