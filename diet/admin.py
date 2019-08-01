"""
Admin interface for the diet application.
"""
from django.contrib import admin

from .models import Person, WeightEntry


class WeightEntry_Admin(admin.ModelAdmin):
    list_display = ['date', 'who', 'weight', 'trend', ]
    list_filter = ['who', ]
    


admin.site.register(WeightEntry, WeightEntry_Admin)
admin.site.register(Person)
