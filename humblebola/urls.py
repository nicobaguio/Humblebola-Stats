from django.conf.urls import url, include

from . import views

player_patterns = [
    url(r'^$',
        views.player_home_page,
        name="player_home_page"),
    url(r'(?P<player_id>[\d]+)-[\w]+-[\w]+/',
        views.player_page,
        name="player_page")
]

tournament_patterns = [
    url(r'^$',
        views.schedule,
        name="schedule")
]

team_patterns = [
    url(r'(?P<team_code>[\w-]+)/', include([
        url(r'^$',
            views.team_home_page,
            name="team_home_page"),
        url(r'(?P<tournament_id>[\d]+)',
            views.team_tournament_page,
            name="team_tournament_page")
        ], namespace="team")),
]

urlpatterns = [
    url(r'^$', views.home_page, name="home_page"),
    url(r'tournaments/', include(
        tournament_patterns, namespace="tournaments")),
    url(r'teams/', include(team_patterns, namespace="teams")),
    url(r'players/', include(player_patterns, namespace="players"))
]
