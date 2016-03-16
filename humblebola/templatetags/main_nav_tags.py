from django import template
from humblebola.models import *

register = template.Library()


@register.inclusion_tag('teams.html')
def show_teams(league):
    teams = Team.objects.filter(league_id=league.id)
    return {'league': league, 'teams': teams}


@register.inclusion_tag('leagues.html')
def show_leagues(league):
    leagues = League.objects.all()
    return {'leagues': leagues}
