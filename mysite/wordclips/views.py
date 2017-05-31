from django.template.loader import get_template
from django.shortcuts import render
from django.template import Context
from django.http import HttpResponse
# from wordclips.wordclip import Wordclip
from wordclips.models import Wordclip
from wordclips.scripts.create_audio import create_audio


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

    # Split the search sentence into words and put into a list
    # wordclip objects
    wl = words.split()
    clips = []
    for w in wl:
        try:
            o = Wordclip.objects.get(name=w)
        except Wordclip.DoesNotExist:
            # TODO: more handling code to nonexist item in the DB
            print(w + " is NOT in the database yet.")
        else:
            print(w + " is in the database.")
            print('path of word ' + w + ' is: ' + o.soundpath)
            clips.append(o)

    # Create the clips

    err, missing = create_audio(wl)
    # Check if there is any missing word in the db
    if err != 0:
        t = get_template('wordclips/error.html')
        html = t.render(Context({ 'missing' : missing }))
        return HttpResponse(html)

    # Print out the results
    print('@@@@@@ input word list')
    for c in clips:
        dis = "%s spoken by %s" % (str(c), str(c.speaker))

        print(dis)

    print('@@@@@@')



    t = get_template('wordclips/page_2.html')
    # html = t.render(Context({ 'clips': clips }))
    html = t.render(Context({}))
    return HttpResponse(html)

def test(request):
    t = get_template('wordclips/page_2.html')
    html = t.render(Context({}))
    return HttpResponse(html)
