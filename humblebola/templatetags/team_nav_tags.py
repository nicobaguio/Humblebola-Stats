from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse, resolve
from django import template
from humblebola.models import *
from humblebola import analytics

register = template.Library()


@register.inclusion_tag('team_nav_bar.html', takes_context=True)
def team_nav_bar(context):
    league = context['league']
    tournament = context['tournament']
    team = context['team']
    request = context['request']
    games = Game.objects.filter(
        league_id=league.id,
        schedule__gt=tournament.start_date,
        schedule__lt=tournament.end_date)

    if league.id == 1:
        try:
            previous_tournament = Tournament.objects.filter(
                league_id=league.id,
                parent_id__isnull=False,
                id__lt=tournament.id,
                ).order_by('-start_date')[0]

            previous_tournament_link = reverse(resolve(
                request.path_info).view_name, args=[
                league.code,
                team.code,
                previous_tournament.id])

        except IndexError:
            previous_tournament = None
            previous_tournament_link = None
        try:
            next_tournament = Tournament.objects.filter(
                league_id=league.id,
                parent_id__isnull=False,
                id__gt=tournament.id,
                ).order_by('start_date')[0]

            next_tournament_link = reverse(resolve(
                request.path_info).view_name, args=[
                league.code,
                team.code,
                next_tournament.id])
        except IndexError:
            next_tournament = None
            next_tournament_link = None
    else:
        try:
            previous_tournament = Tournament.objects.filter(
                league_id=league.id,
                id__lt=tournament.id,
                ).order_by('-start_date')[0]

            previous_tournament_link = reverse(resolve(
                request.path_info).view_name, args=[
                league.code,
                team.code,
                previous_tournament.id])

        except IndexError:
            previous_tournament = None
            previous_tournament_link = None
        try:
            next_tournament = Tournament.objects.filter(
                league_id=league.id,
                id__gt=tournament.id,
                ).order_by('start_date')[0]

            next_tournament_link = reverse(resolve(
                request.path_info).view_name, args=[
                league.code,
                team.code,
                next_tournament.id])

        except IndexError:
            next_tournament = None
            next_tournament_link = None

    record = analytics.get_wins_losses(games, team)
    pace = analytics.get_pace(games, team)
    ortg = analytics.get_eff_ratings(games.filter(game_type=0), 'off', team)
    drtg = analytics.get_eff_ratings(games.filter(game_type=0), 'def', team)

    return {'league': league,
            'team': team,
            'previous_tournament': previous_tournament,
            'next_tournament': next_tournament,
            'previous_tournament_link': previous_tournament_link,
            'next_tournament_link': next_tournament_link,
            'record': record,
            'pace': pace,
            'ortg': ortg,
            'drtg': drtg,
            }
