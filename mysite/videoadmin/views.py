from django.template.loader import get_template
from django.shortcuts import render
from django.template import Context
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required

# Create your views here.
# this login required decorator is to not allow to any
# view without authenticating
@login_required(login_url="login/")
def video_admin(request):
    return render(request,"video_admin.html")
