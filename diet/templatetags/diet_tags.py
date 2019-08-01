"""
Template tags for the people application.
"""
from django import template

from ..utils import get_default_person

#####################################################################

register = template.Library()

#####################################################################

@register.simple_tag(takes_context=True)
def diet_get_person(context):
    request = context.get('request', None)
    if request is None:
        return None
    person = get_default_person(request)
    return person
    
#####################################################################
