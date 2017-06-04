from django.template.loader import get_template
from django.shortcuts import render
from django.template import Context
from django.http import HttpResponse
# from wordclips.wordclip import Wordclip
from wordclips.models import Wordclip
from wordclips.ventriloquy.ventriloquy import Ventriloquy
from wordclips.utils.inputparser import InputParser


# Create your views here.
'''
    Home view
'''
def home(request):
    t = get_template('wordclips/web.html')
    # Populate the context
    html = t.render(Context({}))
    return HttpResponse(html)


'''
    Result view that is returned after text input
'''
def search_in_database(request):

    # Obtain word list
    # print('@@@@ FLAG ')
    words = request.GET.get('Input_text', '')
    # print('receive: ' + wl)

    # Input parser
    parser = InputParser(" ")
    ventriloquy = Ventriloquy()


    # Split the search sentence into words and put into a list
    # wordclip objects
    wl = parser.parse(words)


    # Create the generated video using the clips
    err, missing = ventriloquy.create_audio(wl)
    # Check if there is any missing word in the db
    if err != 0:
        t = get_template('wordclips/error.html')
        html = t.render(Context({ 'missing' : missing }))
        return HttpResponse(html)

    



    t = get_template('wordclips/page_2.html')
    # html = t.render(Context({ 'clips': clips }))
    html = t.render(Context({}))
    return HttpResponse(html)

def test(request):
    t = get_template('wordclips/page_2.html')
    html = t.render(Context({}))
    return HttpResponse(html)
