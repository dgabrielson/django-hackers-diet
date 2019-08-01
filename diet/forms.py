# -*- coding: iso-8859-1 -*-
from django import forms
from django.forms import widgets

from diet.models import WeightEntry


class WeightEntryForm(forms.ModelForm):
    date = forms.DateField()
    weight = forms.FloatField(widget=widgets.NumberInput(
                                    attrs={'inputmode': 'numeric',
                                           'step': '0.1',
                                           'pattern': r"[0-9\.]*",
                                           #'novalidate' :"novalidate"
                                           }))

    class Meta:
        model = WeightEntry
        exclude = ('trend', )
        widgets = {
            'who': forms.HiddenInput,
            }

#
