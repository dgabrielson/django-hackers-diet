# Create your views here.

import datetime
import socket

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, render_to_response
from django.urls import reverse

from .cli import detail
from .forms import WeightEntryForm
from .models import Person, WeightEntry
from .utils import get_default_person

if getattr(settings, 'DIET_NOAUTH', False):
    current_auth = lambda x: x
else:
    current_auth = login_required



class MyActionError(Exception):
    pass



@current_auth
def do_default_save(request):
    form = WeightEntryForm(request.POST)
    if form.is_valid():
        obj = form.save(commit=False)
        # check for an entry for this person for today.
        try:
            check = WeightEntry.objects.filter(who=obj.who, date=obj.date).get()
        except WeightEntry.DoesNotExist:
            # compute trend
            try:
                prev = WeightEntry.objects.filter(who=obj.who, date__lt=obj.date).order_by('-date')[0]
            except IndexError:
                obj.trend = obj.weight
            else:
                obj.trend = prev.trend + 0.1*round(obj.weight - prev.trend)
            obj.save()
            #new_WeightEntry.save_m2m() # not required---no many-to-many data fields.
            # update any future entries trend lines.
            prev = obj
            for obj in WeightEntry.objects.filter(who=obj.who, date__gt=obj.date).order_by('date'):
                obj.trend = prev.trend + 0.1*round(obj.weight - prev.trend)
                obj.save()
                prev = obj
            url = reverse('hackersdiet-bmi',
                          kwargs={'who': obj.who.pk, 'id': obj.pk})
            return HttpResponseRedirect(url)
        else:   # weight entry for today DOES exist
            raise MyActionError('There is already an entry for this person on this day.')
    raise MyActionError('The form was not valid. Try again.')



@current_auth
def do_default_post(request):
    action = request.POST['action']
    person_id = request.POST['who']

    if action == 'Table':
        url = reverse('hackersdiet-table', kwargs={'id': person_id})
        return HttpResponseRedirect(url)

    elif action == 'Stats':
        url = reverse('hackersdiet-stats', kwargs={'id': person_id})
        return HttpResponseRedirect(url)

    elif action == 'Chart':
        url = reverse('hackersdiet-chart', kwargs={'id': person_id})
        return HttpResponseRedirect(url)

    elif action == 'Save':
        return do_default_save(request)

    raise MyActionError('Not a valid action.')



@current_auth
def default(request):
    return default_with_id(request, get_default_person(request) )



@current_auth
def default_with_id(request, id):
    pre_message = ''
    post_message = ''

    if request.method == 'POST':
        # dispatch:
        if not request.POST['who']:
            pre_message = 'You must select a person.'
        else:
            try:
                return do_default_post(request)
            except MyActionError as err:
                pre_message = str(err)


    person = get_default_person(request)
    initial_form_data = {}
    initial_form_data['who'] = person
    initial_form_data['date'] = str(datetime.date.today())
    form = WeightEntryForm(initial= initial_form_data)
    people = Person.objects.all()
    hide_home_url = True
    return render(request, 'diet/default.html', locals())





CHART_HEIGHT = 280
CHART_WIDTH = 320

def chart(request, id):
    person = get_object_or_404(Person, pk=id)
    height = CHART_HEIGHT
    width = CHART_WIDTH
    days = 30
    no_Chart = True
    return render(request, 'diet/chart.html', locals())


@current_auth
def chart_img(request, id, days):
    person = get_object_or_404(Person, pk=id)
    how_much = -int(days)
    img_data = detail.chart(person, how_much, height=CHART_HEIGHT, width=CHART_WIDTH)
    return HttpResponse(img_data, content_type='image/png')



@current_auth
def table(request, id):
    person = get_object_or_404(Person, pk=id)
    no_Table = True
    how_much = -int(30)
    try:
        records = detail.table(person, how_much)
    except IndexError:
        pre_message = 'Error getting data'
    else:
        records.reverse()
    return render(request, 'diet/table.html', locals())


@current_auth
def stats(request, id):
    person = get_object_or_404(Person, pk=id)
    no_Stats = True
    try:
        stats = detail.stats(person)
    except IndexError:
        pre_message = 'Error getting data'
    return render(request, 'diet/stats.html', locals())


@current_auth
def bmi(request, who, id):
    person = get_object_or_404(Person, pk=who)
    entry = get_object_or_404(WeightEntry, pk=id)
    weightBmi, weightBmiDesc = detail.do_bmi(entry.who, entry.weight)
    trendBmi, trendBmiDesc = detail.do_bmi(entry.who, entry.trend)
    print(type(weightBmi), type(trendBmi))
    print(weightBmi, trendBmi)
    return render(request, 'diet/bmi.html', locals())


@current_auth
def bmi_latest(request, who):
    person = get_object_or_404(Person, pk=who)
    qs = WeightEntry.objects.filter(who=person).order_by('-date')
    if qs.exists():
        entry = qs[0]
        return bmi(request, person.id, entry.id)
    else:
        return render(request, 'diet/bmi.html',
                      {'pre_message': 'There is no entry data',
                       'person': person})
#
