import wordclips
import os
from django.template.loader import get_template
from django.shortcuts import render
from django.template import Context
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required

from wordclips.models import Wordclip
from videoadmin.models import CeleryTask


from django.conf import settings

from videoadmin.tasks import UploadTask


# Create your views here.
# this login required decorator is to not allow to any
# view without authenticating
@login_required(login_url="login/")
def video_admin(request):

    # Obtain the keywords to search in the db
    clips_kw = request.GET.get('keyword', 'a')
    APP_ROOT = os.path.abspath(os.path.dirname(wordclips.__file__))
    context = {}

    # Check the validity of the keyword
    if len(clips_kw) == 0:
        return render(request, 'video_admin.html', context)



    #



    # Construct the list contains path of clips
    # of the search of the keyword
    clip_paths = []
    # get a list of objects based on the search
    ol = Wordclip.objects.filter(name__icontains=clips_kw)[0:10]
    for o in ol:
        # construct the full path
        clip_path = settings.MEDIA_URL + o.name + "/1.wav"
        clip_paths.append(o)
        # print(clip_path)

    context = { 'clip_paths' : clip_paths, 'MEDIA_URL' : settings.MEDIA_URL }
    return render(request, 'video_admin.html', context)


def uploaded(request):

    context = {}

    return render(request, 'uploaded.html', context)
