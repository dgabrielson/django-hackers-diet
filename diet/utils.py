
from django.conf import settings

from .models import Person


def get_remote_host_default(request):
    ip = request.META['REMOTE_ADDR']
    try:
        remote_name = socket.gethostbyaddr(ip)[0]
    except:
        return None
    remote_host = remote_name.split('.')[0]    
    try:
        who = Person.objects.get(usual_host__iexact= remote_host)
    except Person.DoesNotExist:
        return None
    return who.id
    
    
def get_user_default(request):
    username = request.user.username
    try:
        who = Person.objects.get(name__iexact=username.lower())
    except Person.DoesNotExist:
        return None
    return who
    

person_discovery_method = getattr(settings, 'DIET_PERSON_DISCOVER', 
                                  'get_user_default')
get_default_person = locals()[person_discovery_method]
