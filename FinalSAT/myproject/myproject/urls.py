from django.conf.urls import patterns, include, url
from django.contrib import admin
from myproject.feedRSS import feedRSS
import settings

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),
	url(r'^$', "DeLorean.views.principalPage"),
	url(r'^login$', "DeLorean.views.logIn"),
	url(r'^logout$', "DeLorean.views.logOut"),
	url(r'^update$', "DeLorean.views.update"),
	url(r'^ayuda$', "DeLorean.views.help"),
	url(r'^todas$', "DeLorean.views.allEvents"),
	url(r'^changeInfo$', "DeLorean.views.changeInfo"),
	url(r'^static/img/(.*)$', "django.views.static.serve", {'document_root': settings.STATIC_URL}),
	url(r'^informacionNoDisponible$', "DeLorean.views.emptyInfo"),
	url(r'^actividades/(.*)$', "DeLorean.views.eventPage"),
	url(r'^like/(.*)$', "DeLorean.views.like"),
	url(r'^add/(.*)$', "DeLorean.views.add"),
	url(r'^(?P<username>.*)/rss$', feedRSS()),
	url(r'^(.*)$', "DeLorean.views.userPage"),
)
