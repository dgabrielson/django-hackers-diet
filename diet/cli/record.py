#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Record your weight.
Compute all relevant items.

Syntax: ./record.py [-w who] [-d when] <what>

Dates are specified YYYY-MM-DD, all numbers.
The current username is used, if -w is not give.
Today is used if -d is not given.
"""
#    Copyright (C) 2006--2009 Dave Gabrielson <dave@gabrielson.ca>
#    This program can be distributed under the terms of the GNU GPL.
#    See the file COPYING.

import datetime
import getopt
# Setup Django environment
import os
import sys
import time

import bmi
from diet.models import Person, WeightEntry

sys.path.insert(0, os.path.expanduser('~/django'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'





def record(who, when, what):
    # add something so we don't add something already here.
    #fp = file('%s.raw.csv' % who, 'at')
    #print >> fp, '%s,%s' % (when, what)

    p = Person.objects.get(name__iexact=who)
    d = datetime.date(*[int(e) for e in when.split('-')])
    w = float(what)
    
    # check for an entry for this person for today.
    try:
        check = WeightEntry.objects.filter(who=p, date=d).get()
    except WeightEntry.DoesNotExist:
        we = WeightEntry(who=p, date=d, weight=w)
        # compute trend
        try:
            prev = WeightEntry.objects.filter(who=p, date__lt=d).order_by('-date')[0]
        except IndexError:
            we.trend = we.weight
        else:
            we.trend = prev.trend + 0.1*round(we.weight - prev.trend)
        # assume there is nothing past today...
        we.save()
        return we
    else:   # weight entry for today DOES exist
        assert False # 'There is already an entry for this person on this day.'




def do_bmi(who, weight):
    p = Person.objects.get(name__iexact=who)

    #feet, inches = file(os.path.join('.', '%s.stature' % who)).read().strip().split('\'')
    feet, inches = p.stature.split('\'')
    height = int(feet)*12.0 + float(inches.strip('"'))
    bmi_f, desc = bmi.bmi_desc(float(weight), height)
    return 'BMI = %.1f (%s)' % (bmi_f, desc)



def main(user, args):
    try:
        opts, noopts = getopt.getopt(args, "w:d:")
    except getopt.GetoptError:
        return __doc__

    who = user
    when = time.strftime('%Y-%m-%d')

    for opt, arg in opts:
        if opt == '-w':
            who = arg
        elif opt == '-d':
            when = arg
        else:
            return __doc__ + "\n\n(Invalid option.)"

    if len(noopts) > 1:
        return __doc__ + "\n\n(You specified more than one [non-option] argument.)"

    who = who.lower()
    what = noopts[0]
    #-----------------

    we = record(who, when, what)
    
    output = 'Weight measurement for %s has been recorded (%s).\n\n' % (who.title(), when)

    output += '\n'
    try:
        output += 'Weight ' + do_bmi(who, what) + '\n'
        if we.trend:
            output += ' Trend ' + do_bmi(who, we.trend) + '\n'
    except IOError:
        output += "[!!!] Can't do BMI until you use set-stature for %s\n" % who

    return output


if __name__ == '__main__':
    print main(os.environ['USER'], sys.argv[1:])
