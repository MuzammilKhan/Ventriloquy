"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from mysite.views import hello, current_datetime, hours_ahead
from wordclips.views import home, search_in_database, test
from videoadmin.views import video_admin
# Add this import
from django.contrib.auth import views
from videoadmin.forms import LoginForm

'''
    Add URL to view function here.
    Remember to import the function from the view files above
'''
urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^time/plus/(\d{1,2})/$', hours_ahead),
    url(r'^$', home),
    url(r'^home/$', home),
    url(r'^home/search/$', search_in_database),
    url(r'^test/$', test),
    url(r'^video_admin/$', video_admin),
    url(r'^login/$', views.login, {'template_name': 'login.html', 'authentication_form': LoginForm}, name='login'),
    url(r'^logout/$', views.logout, {'next_page': '/login'}),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
