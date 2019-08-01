#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Syntax: retrend.py [-w <who>]

"""
#    Copyright (C) 2007--2009 Dave Gabrielson <dave -AT- gabrielson -DOT- ca>
#    This program can be distributed under the terms of the GNU GPL.
#    See the file COPYING.

import getopt
# Setup Django environment
import os
import sys

from diet.models import Person, WeightEntry

sys.path.insert(0, os.path.expanduser('~/django'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'





def retrend(who):
    output = ''
    p = Person.objects.get(name__iexact=who)
    trend = None
    for entry in WeightEntry.objects.filter(who=p).order_by('date'):
        if trend is None:
            trend = entry.weight
        else:
            trend = trend + 0.1*round(entry.weight - trend)
        entry.trend = trend
        print entry
        entry.save()
    return output



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

    if len(noopts) > 0:
        return __doc__ + "\n\n(You specified a [non-option] argument.)"

    who = who.lower()
    return retrend(who)



if __name__ == '__main__':
    import sys,os
    print main(os.environ['USER'], sys.argv[1:])


#
