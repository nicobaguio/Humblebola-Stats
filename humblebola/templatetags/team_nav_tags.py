from django.core.urlresolvers import reverse, resolve
from django import template
from humblebola.models import *
from humblebola import analytics

register = template.Library()


@register.inclusion_tag('team_nav_bar.html', takes_context=True)
def team_nav_bar(context):
    league = context['league']
    current_tournament = context['tournament']
    team = context['team']
    request = context['request']
    games = Game.objects.filter(
        league_id=league.id,
        schedule__gt=current_tournament.start_date,
        schedule__lt=current_tournament.end_date)

    child_tournaments = Tournament.objects.filter(
        league_id=league.id,
        id__in=PlayerTournamentTeam.objects.filter(
            team_id=team.id).distinct('tournament_id').values('tournament_id'))

    parent_tournaments = Tournament.objects.filter(
        id__in=Tournament.objects.filter(
            league_id=league.id,
            id__in=PlayerTournamentTeam.objects.filter(
                team_id=team.id).distinct(
                'tournament_id').values(
                'tournament_id')).values_list('parent_id', flat=True))

    team_tournaments = child_tournaments | parent_tournaments

    tournaments_table = []
    for tournament in team_tournaments.order_by('start_date', 'id'):
        tournaments_table.append({'tournament': tournament})

    # Handle context based previous & next tournament link. Built-in handler
    # for PBA so it doesn't include parent tournament.

    if league.id == 1:
        try:
            previous_tournament = Tournament.objects.filter(
                league_id=league.id,
                parent_id__isnull=False,
                id__lt=current_tournament.id,
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
                id__gt=current_tournament.id,
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
                id__lt=current_tournament.id,
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
                id__gt=current_tournament.id,
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
            'current_tournament': current_tournament,
            'previous_tournament': previous_tournament,
            'next_tournament': next_tournament,
            'previous_tournament_link': previous_tournament_link,
            'next_tournament_link': next_tournament_link,
            'tournaments_table': tournaments_table,
            'record': record,
            'pace': pace,
            'ortg': ortg,
            'drtg': drtg,
            }
