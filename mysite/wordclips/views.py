from django.template.loader import get_template
from django.shortcuts import render
from django.template import Context
from django.http import HttpResponse
from wordclips.wordclip import Wordclip

# Create your views here.
'''
    View that returns the current datetime
'''
def home(request):
    t = get_template('wordclips/web.html')
    # Populate the context
    html = t.render(Context({}))
    return HttpResponse(html)


def search_in_database(request):

    # Obtain word list
    # print('@@@@ FLAG ')
    words = request.GET.get('searchtext', '');
    # print('receive: ' + wl)

    # Split the search sentence into words and put into a list
    wl = words.split()
    clips = []
    for w in wl:
        clips.append(Wordclip(w, ""))

    # TODO Searching the word list in the database

    


    t = get_template('wordclips/page_2.html')
    # html = t.render(Context({ 'clips': clips }))
    html = t.render(Context({}))
    return HttpResponse(html)

def test(request):
    t = get_template('wordclips/page_2.html')
    html = t.render(Context({}))
    return HttpResponse(html)
