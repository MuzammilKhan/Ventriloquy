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
from videoadmin.tasks import get_task_status
from videoadmin.tasks import process

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
    ol = CeleryTask.objects.filter(celery_task_status=u'PROGRESS')
    for o in ol :
        if get_task_status(o.celery_task_id)['status'] == u'SUCCESS':
            o.celery_task_status=u'SUCCESS'
            o.save()


    task_list = []
    ol = CeleryTask.objects.all()[0:10]
    for o in ol:
        task_list.append(o)


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

    context = { 'clip_paths' : clip_paths,
                'MEDIA_URL' : settings.MEDIA_URL,
                'task_list' : task_list, }
    return render(request, 'video_admin.html', context)


def uploaded(request):

    # Obtain the uploaded video




    # t = UploadTask.delay("Hello World")
    # t = process.delay('obama', '/some/path')

    # celery_task = CeleryTask(celery_task_id=t.id, celery_task_status = u'PROGRESS')
    # celery_task.save()

    context = {}

    return render(request, 'uploaded.html', context)
