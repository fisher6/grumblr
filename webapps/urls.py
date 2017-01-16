from django.conf.urls import include, url
from django.contrib import admin

import grumblr.views

urlpatterns = [
	url(r'^admin/', admin.site.urls),
	url(r'^', include('grumblr.urls')), # redirect every url to grumblr app URLS
]
