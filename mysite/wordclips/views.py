from django.template.loader import get_template
from django.shortcuts import render
from django.template import Context
from django.http import HttpResponse

# Create your views here.
'''
    View that returns the current datetime
'''
def home(request):
    t = get_template('wordclips/home.html')
    # Populate the context
    html = t.render(Context({}))
    return HttpResponse(html)


def search_in_database(request):
    t = get_template('wordclips/search.html')
    html = t.render(Context({}))
    return HttpResponse(html)
