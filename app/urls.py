from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from . import views
import re

app_name = 'app'
urlpatterns = [
	url(r'^hw/$', views.index),
	url(r'^news(/\d{7}.html)$',views.getnews),
	url(r'^team(/team_\d{2,3}.html)$',views.getteam),
	url(r'^index.html',views.findindex,name='findindex'),
	url(r'^search/', views.search, name='search'),
	url(r'^result/(?P<text>.+)/', views.result, name='result'),
]
