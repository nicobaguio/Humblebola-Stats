from django.shortcuts import get_object_or_404, render, redirect
from decimal import Decimal
from .models import *

from datetime import date, datetime, time

from humblebola import analytics
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
        wins_and_losses = analytics.get_wins_losses(current_games, team)
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
        wins_and_losses = analytics.get_wins_losses(current_games, team)
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

        total_table_dict = analytics.get_player_stat(
            current_games,
            player,
            'totals')

        total_table_dict.update({
            'tournament': tournament,
            'age': age,
            'teams': " / ".join(teams) if len(teams) > 0 else "TOT",
            'pos': pos
            })

        total_table.append(total_table_dict)

        per_game_table_dict = analytics.get_player_stat(
            current_games,
            player,
            'per_game')

        per_game_table_dict.update({
            'tournament': tournament,
            'age': age,
            'teams': " / ".join(teams) if len(teams) > 0 else "TOT",
            'pos': pos
            })

        per_game_table.append(per_game_table_dict)

        per_three_six_table_dict = analytics.get_player_stat(
            current_games,
            player,
            'per_three_six')

        per_three_six_table_dict.update({
            'tournament': tournament,
            'age': age,
            'teams': " / ".join(teams) if len(teams) > 0 else "TOT",
            'pos': pos
            })

        per_three_six_table.append(per_three_six_table_dict)

    return render(request, 'humblebola/player_page.html', {
        'league': league,
        'player': player,
        'total_table': total_table,
        'per_game_table': per_game_table,
        'per_three_six_table': per_three_six_table})


def team_index_page(request, code, team_code):
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

        wins_and_losses = analytics.get_wins_losses(current_games, team)
        win = wins_and_losses['win']
        loss = wins_and_losses['loss']
        win_p = wins_and_losses['win_p']
        pace = analytics.get_pace(current_games.filter(game_type=0), team)
        rel_pace = analytics.get_pace(current_games.filter(game_type=0)) - pace
        ortg = analytics.get_eff_ratings(current_games.filter(
            game_type=0), 'off', team)
        drtg = analytics.get_eff_ratings(current_games.filter(
            game_type=0), 'def', team)
        rtg = analytics.get_eff_ratings(current_games.filter(
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

    return render(request, 'humblebola/team_page/team_index_page.html', {
        'league': league,
        'team': team,
        'seasons': parent_tournaments if code == 'pba' else child_tournaments,
        'table': table})


def team_tournament_page(request, code, team_code, tournament_id):
    league = get_object_or_404(League, code=code)
    team = get_object_or_404(Team, code=team_code)
    tournament = get_object_or_404(Tournament, id=tournament_id)
    players = Player.objects.filter(
        id__in=PlayerTournamentTeam.objects.filter(
            tournament_id=tournament.id,
            team_id=team.id).values_list('player_id', flat=True))

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

        except IndexError:
            previous_tournament = None
        try:
            next_tournament = Tournament.objects.filter(
                league_id=league.id,
                parent_id__isnull=False,
                id__gt=tournament.id,
                ).order_by('start_date')[0]
        except IndexError:
            next_tournament = None
    else:
        try:
            previous_tournament = Tournament.objects.filter(
                league_id=league.id,
                id__lt=tournament.id,
                ).order_by('-start_date')[0]

        except IndexError:
            previous_tournament = None
        try:
            next_tournament = Tournament.objects.filter(
                league_id=league.id,
                id__gt=tournament.id,
                ).order_by('start_date')[0]
        except IndexError:
            next_tournament = None

    record = analytics.get_wins_losses(games, team)
    pace = analytics.get_pace(games, team)
    ortg = analytics.get_eff_ratings(games.filter(game_type=0), 'off', team)
    drtg = analytics.get_eff_ratings(games.filter(game_type=0), 'def', team)
    team_total_table = analytics.get_team_stat(
            games.filter(game_type=0),
            team,
            'totals')
    team_per_game_table = analytics.get_team_stat(
        games.filter(game_type=0),
        team,
        'per_game')
    team_adv_table = analytics.get_team_stat(
        games.filter(game_type=0),
        team,
        'adv')
    opp_team_total_table = analytics.get_team_stat(
            games.filter(game_type=0),
            team,
            'totals',
            'opp')
    opp_team_per_game_table = analytics.get_team_stat(
        games.filter(game_type=0),
        team,
        'per_game',
        'opp')

    player_totals_table = []
    player_per_game_table = []
    player_per_three_six_table = []

    for player in players.order_by('last_name', 'first_name'):
        player_age = player.get_age(tournament.start_date, 0)

        player_totals_dict = analytics.get_player_stat(
            games,
            player,
            'totals')

        player_per_game_dict = analytics.get_player_stat(
            games,
            player,
            'per_game')

        player_per_three_six_dict = analytics.get_player_stat(
            games,
            player,
            'per_three_six')

        player_totals_dict.update({
            'full_name': player.first_name + " " + player.last_name,
            'age': player_age,
            'player': player,
            })

        player_totals_table.append(player_totals_dict)

        player_per_game_dict.update({
            'full_name': player.first_name + " " + player.last_name,
            'age': player_age,
            'player': player,
            })

        player_per_game_table.append(player_per_game_dict)

        player_per_three_six_dict.update({
            'full_name': player.first_name + " " + player.last_name,
            'age': player_age,
            'player': player,
            })

        player_per_three_six_table.append(player_per_three_six_dict)

    return render(request, 'humblebola/team_page/team_tournament_page.html', {
        'league': league,
        'team': team,
        'tournament': tournament,
        'previous_tournament': previous_tournament,
        'next_tournament': next_tournament,
        'record': record,
        'pace': pace,
        'ortg': ortg,
        'drtg': drtg,
        'players': players,
        'team_total_table': team_total_table,
        'team_per_game_table': team_per_game_table,
        'team_adv_table': team_adv_table,
        'opp_team_total_table': opp_team_total_table,
        'opp_team_per_game_table': opp_team_per_game_table,
        'player_totals_table': player_totals_table,
        'player_per_game_table': player_per_game_table,
        'player_per_three_six_table': player_per_three_six_table,
        })


def team_schedule_page(request, code, team_code, tournament_id):
    league = get_object_or_404(League, code=code)
    team = get_object_or_404(Team, code=team_code)
    tournament = get_object_or_404(Tournament, id=tournament_id)

    home_games = Game.objects.filter(
        league_id=league.id,
        schedule__gt=tournament.start_date,
        schedule__lt=tournament.end_date,
        home_team_id=team.id)

    away_games = Game.objects.filter(
        league_id=league.id,
        schedule__gt=tournament.start_date,
        schedule__lt=tournament.end_date,
        away_team_id=team.id)

    games = home_games | away_games

    return render(request, 'humblebola/team_page/team_schedule_page.html', {
        'league': league,
        'team': team,
        'tournament': tournament,
        'regular_games': games.filter(game_type=0).order_by('schedule'),
        'playoff_games': games.filter(game_type=1).order_by('schedule'),
        })


def team_tournament_game_log(request, code, team_code, tournament_id):
    league = get_object_or_404(League, code=code)
    team = get_object_or_404(Team, code=team_code)
    tournament = get_object_or_404(Tournament, id=tournament_id)

    home_games = Game.objects.filter(
        league_id=league.id,
        schedule__gt=tournament.start_date,
        schedule__lt=tournament.end_date,
        home_team_id=team.id)

    away_games = Game.objects.filter(
        league_id=league.id,
        schedule__gt=tournament.start_date,
        schedule__lt=tournament.end_date,
        away_team_id=team.id)

    games = home_games | away_games

    regular_game_totals_table = []
    playoff_game_totals_table = []

    for game in games.order_by('schedule'):
        if game.game_type == 0:
            team_game_stat = GameTeamStat.objects.filter(
                game_id=game.id,
                team_id=team.id)

            opp_team_game_stat = GameTeamStat.objects.filter(
                game_id=game.id,
                opp_team_id=team.id)

            team_game_stat_dict = analytics.get_stat(team_game_stat)
            opp_team_game_stat_dict = analytics.get_stat(opp_team_game_stat)

            team_game_stat_dict.update({
                'game': game,
                'opp_total_points_scored': opp_team_game_stat_dict[
                    'total_points_scored'],
                'opp_total_fg_made': opp_team_game_stat_dict[
                    'total_fg_made'],
                'opp_total_fg_attempts': opp_team_game_stat_dict[
                    'total_fg_attempts'],
                'opp_fg_percent': opp_team_game_stat_dict[
                    'fg_percent'],
                'opp_total_three_pt_made': opp_team_game_stat_dict[
                    'total_three_pt_made'],
                'opp_total_three_pt_attempts': opp_team_game_stat_dict[
                    'total_three_pt_attempts'],
                'opp_three_pt_percent': opp_team_game_stat_dict[
                    'three_pt_percent'],
                'opp_total_ft_made': opp_team_game_stat_dict[
                    'total_ft_made'],
                'opp_total_ft_attempts': opp_team_game_stat_dict[
                    'total_ft_attempts'],
                'opp_ft_percent': opp_team_game_stat_dict[
                    'ft_percent'],
                'opp_total_offensive_reb': opp_team_game_stat_dict[
                    'total_offensive_reb'],
                'opp_total_defensive_reb': opp_team_game_stat_dict[
                    'total_defensive_reb'],
                'opp_total_assists': opp_team_game_stat_dict[
                    'total_assists'],
                'opp_total_steals': opp_team_game_stat_dict[
                    'total_steals'],
                'opp_total_blocks': opp_team_game_stat_dict[
                    'total_blocks'],
                'opp_total_turnovers': opp_team_game_stat_dict[
                    'total_turnovers'],
                'opp_total_personal_fouls': opp_team_game_stat_dict[
                    'total_personal_fouls'],
                })

            regular_game_totals_table.append(team_game_stat_dict)

        elif game.game_type == 1:
            team_game_stat = GameTeamStat.objects.filter(
                game_id=game.id,
                team_id=team.id)

            opp_team_game_stat = GameTeamStat.objects.filter(
                game_id=game.id,
                opp_team_id=team.id)

            team_game_stat_dict = analytics.get_stat(team_game_stat)
            opp_team_game_stat_dict = analytics.get_stat(opp_team_game_stat)

            team_game_stat_dict.update({
                'game': game,
                'opp_total_points_scored': opp_team_game_stat_dict[
                    'total_points_scored'],
                'opp_total_fg_made': opp_team_game_stat_dict[
                    'total_fg_made'],
                'opp_total_fg_attempts': opp_team_game_stat_dict[
                    'total_fg_attempts'],
                'opp_fg_percent': opp_team_game_stat_dict[
                    'fg_percent'],
                'opp_total_three_pt_made': opp_team_game_stat_dict[
                    'total_three_pt_made'],
                'opp_total_three_pt_attempts': opp_team_game_stat_dict[
                    'total_three_pt_attempts'],
                'opp_three_pt_percent': opp_team_game_stat_dict[
                    'three_pt_percent'],
                'opp_total_ft_made': opp_team_game_stat_dict[
                    'total_ft_made'],
                'opp_total_ft_attempts': opp_team_game_stat_dict[
                    'total_ft_attempts'],
                'opp_ft_percent': opp_team_game_stat_dict[
                    'ft_percent'],
                'opp_total_offensive_reb': opp_team_game_stat_dict[
                    'total_offensive_reb'],
                'opp_total_defensive_reb': opp_team_game_stat_dict[
                    'total_defensive_reb'],
                'opp_total_assists': opp_team_game_stat_dict[
                    'total_assists'],
                'opp_total_steals': opp_team_game_stat_dict[
                    'total_steals'],
                'opp_total_blocks': opp_team_game_stat_dict[
                    'total_blocks'],
                'opp_total_turnovers': opp_team_game_stat_dict[
                    'total_turnovers'],
                'opp_total_personal_fouls': opp_team_game_stat_dict[
                    'total_personal_fouls'],
                })


            playoff_game_totals_table.append(team_game_stat_dict)

    return render(request,
                  'humblebola/team_page/team_tournament_game_log.html', {
                    'league': league,
                    'team': team,
                    'tournament': tournament,
                    'regular_game_totals_table': regular_game_totals_table,
                    'playoff_game_totals_table': playoff_game_totals_table,
                    })
