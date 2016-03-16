from django.shortcuts import get_object_or_404, render

from .models import *
from datetime import date, datetime, time

from humblebola import functions
# Create your views here.


def home_page(request, code):
    league = get_object_or_404(League, code=code)

    if code == 'pba':
        current_tournament = Tournament.objects.get(
            league_id=league.id,
            start_date__lt=date.today(),
            end_date__gt=date.today(),
            parent_id__gt=0)
    else:
        current_tournament = Tournament.objects.filter(
            league_id=league.id).order_by('-end_date')[0]

    current_games = Game.objects.filter(
        league_id=league.id,
        schedule__gt=current_tournament.start_date,
        schedule__lt=current_tournament.end_date).order_by('schedule')

    if date.today() > current_tournament.end_date:
        next_game = iter([])
        prev_game = iter([])
    else:
        next_game_date = current_games.filter(
            schedule__gt=date.today()).order_by('schedule')[0].schedule.date()

        next_game = Game.objects.filter(
            league_id=league.id,
            schedule__range=(datetime.combine(next_game_date, time.min),
                             datetime.combine(next_game_date, time.max)))

        prev_game_date = current_games.filter(
            schedule__lt=next_game[0].schedule).order_by(
            '-schedule')[0].schedule.date()

        prev_game = Game.objects.filter(
            league_id=league.id,
            schedule__range=(datetime.combine(prev_game_date, time.min),
                             datetime.combine(prev_game_date, time.max)))

    standings = []

    for team in Team.objects.filter(league_id=league.id):
        wins_and_losses = functions.get_wins_losses(current_games, team)
        win = wins_and_losses['win']
        loss = wins_and_losses['loss']
        win_p = wins_and_losses['win_p']

        standings.append({'team': team.code,
                          'win': win,
                          'loss': loss,
                          'win_p': win_p})

    return render(request, 'humblebola/home_page.html', {
        'league': league,
        'tournament': current_tournament,
        'next_game': next_game,
        'prev_game': prev_game,
        'standings': standings,
        'regular_games': current_games.filter(game_type=0),
        'playoff_games': current_games.filter(game_type=1),
        'teams': Team.objects.filter(league_id=league.id)})


def schedule(request, code, tournament_id=None):
    league = get_object_or_404(League, code=code)

    if code == 'pba':
        current_tournament = Tournament.objects.get(
            league_id=league.id,
            start_date__lt=date.today(),
            end_date__gt=date.today(),
            parent_id__gt=0)
    else:
        current_tournament = Tournament.objects.filter(
            league_id=league.id).order_by('-end_date')[0]

    current_games = Game.objects.filter(
        league_id=league.id,
        schedule__gt=current_tournament.start_date,
        schedule__lt=current_tournament.end_date).order_by('schedule')

    if date.today() > current_tournament.end_date:
        next_game = iter([])
        prev_game = iter([])
    else:
        next_game_date = current_games.filter(
            schedule__gt=date.today()).order_by('schedule')[0].schedule.date()

        next_game = Game.objects.filter(
            league_id=league.id,
            schedule__range=(datetime.combine(next_game_date, time.min),
                             datetime.combine(next_game_date, time.max)))

        prev_game_date = current_games.filter(
            schedule__lt=next_game[0].schedule).order_by(
            '-schedule')[0].schedule.date()

        prev_game = Game.objects.filter(
            league_id=league.id,
            schedule__range=(datetime.combine(prev_game_date, time.min),
                             datetime.combine(prev_game_date, time.max)))
    standings = []

    for team in Team.objects.filter(league_id=league.id):
        wins_and_losses = functions.get_wins_losses(current_games, team)
        win = wins_and_losses['win']
        loss = wins_and_losses['loss']
        win_p = wins_and_losses['win_p']

        standings.append({'team': team.code,
                          'win': win,
                          'loss': loss,
                          'win_p': win_p})

    return render(request, 'humblebola/schedule.html', {
        'league': league,
        'next_game': next_game,
        'prev_game': prev_game,
        'standings': standings,
        'regular_games': current_games.filter(game_type=0),
        'playoff_games': current_games.filter(game_type=1),
        'teams': Team.objects.filter(league_id=league.id)})


def team_home_page(request, code, team_code):
    league = get_object_or_404(League, code=code)
    team = get_object_or_404(Team, code=team_code)
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

    standings = []

    for tournament in team_tournaments.order_by('start_date', 'id'):
        current_games = Game.objects.filter(
            league_id=league.id,
            schedule__gt=tournament.start_date,
            schedule__lt=tournament.end_date)

        wins_and_losses = functions.get_wins_losses(current_games, team)
        win = wins_and_losses['win']
        loss = wins_and_losses['loss']
        win_p = wins_and_losses['win_p']
        pace = functions.get_pace(current_games.filter(game_type=0), team)
        rel_pace = functions.get_pace(current_games.filter(game_type=0)) - pace
        ortg = functions.team_get_ratings(current_games.filter(
            game_type=0), 'off', team)
        drtg = functions.team_get_ratings(current_games.filter(
            game_type=0), 'def', team)
        rtg = functions.team_get_ratings(current_games.filter(
            game_type=0))

        standings.append({'tournament': tournament,
                          'win': win,
                          'loss': loss,
                          'win_p': win_p,
                          'pace': pace,
                          'rel_pace': rel_pace,
                          'ortg': ortg,
                          'rel_ortg': ortg - rtg,
                          'drtg': drtg,
                          'rel_drtg': drtg - rtg})

    return render(request, 'humblebola/team_home_page.html', {
        'league': league,
        'team': team,
        'seasons': parent_tournaments if code == 'pba' else child_tournaments,
        'standings': standings})


def player_home_page(request, code):
    league = get_object_or_404(League, code=code)

    if code == 'pba':
        current_tournament = Tournament.objects.get(
            league_id=league.id,
            start_date__lt=date.today(),
            end_date__gt=date.today(),
            parent_id__gt=0)
    else:
        current_tournament = Tournament.objects.filter(
            league_id=league.id).order_by('-end_date')[0]

    current_players = Player.objects.filter(
        id__in=PlayerTournamentTeam.objects.filter(
            tournament_id=current_tournament.id).values_list(
            'player_id', flat=True)).order_by('last_name', 'first_name')

    return render(request, 'humblebola/player_home_page.html', {
        'league': league,
        'players': current_players})
