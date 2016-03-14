from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home_page, name="home_page"),
    url(r'games/$', views.schedule, name="schedule"),
    url(r'teams/(?P<team_code>\w+)/', views.team_home_page, name="team_home_page"),
]
