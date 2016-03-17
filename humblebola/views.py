from django.shortcuts import get_object_or_404, render, redirect

from django.db.models import Sum
from .models import *

from datetime import date, datetime, time

from decimal import Decimal

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

    table = []

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

        table.append({'tournament': tournament,
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
        'table': table})


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


def player_page(request, code, player_id):
    league = get_object_or_404(League, code=code)
    player = get_object_or_404(Player, id=player_id)

    if request.path != player.get_absolute_url():
        return redirect(player)

    child_tournaments = Tournament.objects.filter(
        league_id=league.id,
        id__in=PlayerTournamentTeam.objects.filter(
            player_id=player.id).values('tournament_id'))

    parent_tournaments = Tournament.objects.filter(
        id__in=Tournament.objects.filter(
            league_id=league.id,
            id__in=PlayerTournamentTeam.objects.filter(
                player_id=player.id).values(
                'tournament_id')).values_list('parent_id', flat=True))

    player_tournaments = child_tournaments | parent_tournaments

    total_table = []
    per_game_table = []
    per_three_six_table = []

    for tournament in player_tournaments.order_by('start_date', 'id'):
        current_games = Game.objects.filter(
            league_id=league.id,
            schedule__gt=tournament.start_date,
            schedule__lt=tournament.end_date)

        age = player.get_age(tournament.start_date)

        items = PlayerTournamentTeam.objects.filter(
                player_id=player.id, tournament_id=tournament.id)

        teams = []

        for item in items:
            teams.append(item.team.code)

        if player.position.lower() != 'center':
            pos = player.position.split(" ")[0][0].upper() + \
                  player.position.split(" ")[1][0].upper()
        else:
            pos = 'C'

        player_reg_games = GamePlayerStat.objects.filter(
            player_id=player.id,
            game_id__in=current_games.filter(
                game_type=0).values_list('id', flat=True),
            seconds_played__gt=0)

        games_played = player_reg_games.count()

        games_started = player_reg_games.filter(started="True").count()

        total_minutes_played = (Decimal(player_reg_games.aggregate(
            Sum('seconds_played'))['seconds_played__sum']) /
            60).quantize(Decimal(10)**-1)

        if league.id == 1:
            adjusted_minutes = 36 / total_minutes_played
        else:
            adjusted_minutes = 30 / total_minutes_played

        total_points_scored = Decimal(player_reg_games.aggregate(
            Sum('ft_made'))['ft_made__sum']) + \
            Decimal(player_reg_games.aggregate(
                Sum('fg_made'))['fg_made__sum']) * 2 + \
            Decimal(player_reg_games.aggregate(
                Sum('three_pt_made'))['three_pt_made__sum'])

        total_fg_made = Decimal(player_reg_games.aggregate(
            Sum('fg_made'))['fg_made__sum'])

        total_fg_attempts = Decimal(player_reg_games.aggregate(
            Sum('fg_attempts'))['fg_attempts__sum'])

        if total_fg_attempts > 0:
            fg_percent = ((total_fg_made/total_fg_attempts) *
                          100).quantize(Decimal(10)**-1)
        else:
            fg_percent = Decimal(0.0).quantize(Decimal(10)**-1)

        total_three_pt_made = Decimal(player_reg_games.aggregate(
            Sum('three_pt_made'))['three_pt_made__sum'])

        total_three_pt_attempts = Decimal(player_reg_games.aggregate(
            Sum('three_pt_attempts'))['three_pt_attempts__sum'])

        if total_three_pt_attempts > 0:
            three_pt_percent = ((total_three_pt_made/total_three_pt_attempts) *
                                100).quantize(Decimal(10)**-1)
        else:
            three_pt_percent = Decimal(0.0).quantize(Decimal(10)**-1)

        total_ft_made = Decimal(player_reg_games.aggregate(
            Sum('ft_made'))['ft_made__sum'])

        total_ft_attempts = Decimal(player_reg_games.aggregate(
            Sum('ft_attempts'))['ft_attempts__sum'])

        if total_ft_attempts > 0:
            ft_percent = ((total_ft_made/total_ft_attempts) *
                          100).quantize(Decimal(10)**-1)
        else:
            ft_percent = Decimal(0.0).quantize(Decimal(10)**-1)

        total_offensive_reb = Decimal(player_reg_games.aggregate(
            Sum('offensive_reb'))['offensive_reb__sum'])

        total_defensive_reb = Decimal(player_reg_games.aggregate(
            Sum('defensive_reb'))['defensive_reb__sum'])

        total_assists = Decimal(player_reg_games.aggregate(
            Sum('assists'))['assists__sum'])

        total_steals = Decimal(player_reg_games.aggregate(
            Sum('steals'))['steals__sum'])

        total_blocks = Decimal(player_reg_games.aggregate(
            Sum('blocks'))['blocks__sum'])

        total_turnovers = Decimal(player_reg_games.aggregate(
            Sum('turnovers'))['turnovers__sum'])

        total_personal_fouls = Decimal(player_reg_games.aggregate(
            Sum('personal_fouls'))['personal_fouls__sum'])

        total_table.append({
            'tournament': tournament,
            'age': age,
            'teams': " / ".join(teams) if len(teams) > 0 else "TOT",
            'pos': pos,
            'games_played': games_played,
            'games_started': games_started,
            'minutes_played': total_minutes_played,
            'points_scored': total_points_scored,
            'fg_made': total_fg_made,
            'fg_attempts': total_fg_attempts,
            'fg_percent': fg_percent,
            'three_pt_made': total_three_pt_made,
            'three_pt_attempts': total_three_pt_attempts,
            'three_pt_percent': three_pt_percent,
            'ft_made': total_ft_made,
            'ft_attempts': total_ft_attempts,
            'ft_percent': ft_percent,
            'offensive_reb': total_offensive_reb,
            'defensive_reb': total_defensive_reb,
            'reb': total_offensive_reb + total_defensive_reb,
            'assists': total_assists,
            'steals': total_steals,
            'blocks': total_blocks,
            'turnovers': total_turnovers,
            'personal_fouls': total_personal_fouls})

        per_game_table.append({
            'tournament': tournament,
            'age': age,
            'teams': " / ".join(teams) if len(teams) > 0 else "TOT",
            'pos': pos,
            'games_played': games_played,
            'games_started': games_started,
            'minutes_played': (total_minutes_played /
                              Decimal(games_played)).quantize(
                              Decimal(10)**-1),
            'points_scored': (total_points_scored /
                              Decimal(games_played)).quantize(
                              Decimal(10)**-1),
            'fg_made': (total_fg_made /
                        Decimal(games_played)).quantize(
                        Decimal(10)**-1),
            'fg_attempts': (total_fg_attempts /
                            Decimal(games_played)).quantize(
                            Decimal(10)**-1),
            'fg_percent': fg_percent,
            'three_pt_made': (total_three_pt_made /
                              Decimal(games_played)).quantize(
                              Decimal(10)**-1),
            'three_pt_attempts': (total_three_pt_attempts /
                                  Decimal(games_played)).quantize(
                                  Decimal(10)**-1),
            'three_pt_percent': three_pt_percent,
            'ft_made': (total_ft_made /
                        Decimal(games_played)).quantize(
                        Decimal(10)**-1),
            'ft_attempts': (total_ft_attempts /
                            Decimal(games_played)).quantize(
                            Decimal(10)**-1),
            'ft_percent': ft_percent,
            'offensive_reb': (total_offensive_reb /
                              Decimal(games_played)).quantize(
                              Decimal(10)**-1),
            'defensive_reb': (total_defensive_reb /
                              Decimal(games_played)).quantize(
                              Decimal(10)**-1),
            'reb': ((total_offensive_reb + total_defensive_reb) /
                    Decimal(games_played)).quantize(
                    Decimal(10)**-1),
            'assists': (total_assists /
                                  Decimal(games_played)).quantize(
                                  Decimal(10)**-1),
            'steals': (total_steals /
                       Decimal(games_played)).quantize(
                       Decimal(10)**-1),
            'blocks': (total_blocks /
                       Decimal(games_played)).quantize(
                       Decimal(10)**-1),
            'turnovers': (total_turnovers /
                          Decimal(games_played)).quantize(
                          Decimal(10)**-1),
            'personal_fouls': (total_personal_fouls /
                               Decimal(games_played)).quantize(
                               Decimal(10)**-1)})

        per_three_six_table.append({
            'tournament': tournament,
            'age': age,
            'teams': " / ".join(teams) if len(teams) > 0 else "TOT",
            'pos': pos,
            'games_played': games_played,
            'games_started': games_started,
            'minutes_played': (total_minutes_played /
                               Decimal(games_played)).quantize(
                               Decimal(10)**-1),
            'points_scored': (adjusted_minutes * total_points_scored).quantize(
                Decimal(10)**-1),
            'fg_made': (adjusted_minutes * total_fg_made).quantize(
                Decimal(10)**-1),
            'fg_attempts': (adjusted_minutes * total_fg_attempts).quantize(
                Decimal(10)**-1),
            'fg_percent': fg_percent,
            'three_pt_made': (adjusted_minutes * total_three_pt_made).quantize(
                Decimal(10)**-1),
            'three_pt_attempts': (adjusted_minutes *
                                  total_three_pt_attempts).quantize(
                                  Decimal(10)**-1),
            'three_pt_percent': three_pt_percent,
            'ft_made': (adjusted_minutes * total_ft_made).quantize(
                Decimal(10)**-1),
            'ft_attempts': (adjusted_minutes * total_ft_attempts).quantize(
                Decimal(10)**-1),
            'ft_percent': ft_percent,
            'offensive_reb': (adjusted_minutes * total_offensive_reb).quantize(
                Decimal(10)**-1),
            'defensive_reb': (adjusted_minutes * total_defensive_reb).quantize(
                Decimal(10)**-1),
            'reb': (adjusted_minutes *
                    (total_offensive_reb + total_defensive_reb)).quantize(
                    Decimal(10)**-1),
            'assists': (adjusted_minutes * total_assists).quantize(
                Decimal(10)**-1),
            'steals': (adjusted_minutes * total_steals).quantize(
                Decimal(10)**-1),
            'blocks': (adjusted_minutes * total_blocks).quantize(
                Decimal(10)**-1),
            'turnovers': (adjusted_minutes * total_turnovers).quantize(
                Decimal(10)**-1),
            'personal_fouls': (adjusted_minutes *
                               total_personal_fouls).quantize(
                               Decimal(10)**-1)})

    return render(request, 'humblebola/player_page.html', {
        'league': league,
        'player': player,
        'total_table': total_table,
        'per_game_table': per_game_table,
        'per_three_six_table': per_three_six_table})
