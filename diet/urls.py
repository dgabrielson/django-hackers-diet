
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', 
        views.default,
        name='hackersdiet-default',
        ),
    url(r'^(?P<id>\d+)/$',  
        views.default_with_id,
        name='hackersdiet-default-id',
        ),
    url(r'^(?P<id>\d+)/table/$',  
        views.table,
        name='hackersdiet-table',
        ),
    url(r'^(?P<id>\d+)/stats/$',  
        views.stats,
        name='hackersdiet-stats',
        ),
    url(r'^(?P<id>\d+)/chart/$',  
        views.chart,
        name='hackersdiet-chart',
        ),
    url(r'^(?P<id>\d+)/chart/img/(?P<days>\d+)/$',  
        views.chart_img,
        name='hackersdiet-chart-img',
        ),
    url(r'^(?P<who>\d+)/bmi/(?P<id>\d+)/$',  
        views.bmi,
        name='hackersdiet-bmi',
        ),
    url(r'^(?P<who>\d+)/bmi/$',  
        views.bmi_latest,
        name='hackersdiet-bmi-latest',
        ),
    ]
