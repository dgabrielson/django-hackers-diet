#!/usr/bin/env python
#######################
from __future__ import print_function, unicode_literals

#######################
"""
Compute BMI, and description.


    *  Underweight = <18.5
    * Normal weight = 18.5-24.9
    * Overweight = 25-29.9
    * Obesity = BMI of 30 or greater


Imperial:
    BMI = 703*lb/in^2
Metric:
    10000*kg/cm^2
"""
#    Copyright (C) 2006--2009 Dave Gabrielson <dave@gabrielson.ca>
#    This program can be distributed under the terms of the GNU GPL.
#    See the file COPYING.

def imperial(lbs, inches):
    return 703.0*lbs/(inches**2)


def metric(kgs, cms):
    return 10000.0*kgs/(cms**2)

def description(bmi):
    if bmi < 18.5:
        return 'underweight'
    elif 18.5 <= bmi < 25.0:
        return 'normal weight'
    elif 25.0 <= bmi < 30.0:
        return 'overweight'
    else:
        return 'obese'


def bmi_desc(weight, height, measure= imperial):
    bmi = measure(weight, height)
    desc = description(bmi)
    return bmi, desc


def main(args):
    weight = float(args[0])
    height = float(args[1])

    bmi, desc = bmi_desc(weight, height)

    print('BMI = %.1f' % bmi, '(%s)' % desc)


if __name__ == '__main__':
    import sys
    try:
        main(sys.argv[1:])
    except IndexError:
        print('''
bmi.py

Compute BMI and a description.

Syntax:
	bmi.py <weight in pounds> <height in inches>

''')
