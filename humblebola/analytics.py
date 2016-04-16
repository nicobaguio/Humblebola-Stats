from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.db.models import F, Sum, Avg

from humblebola.models import *

# Returns a dict of wins/losses/win_p of a team in a given set of games.


def get_wins_losses(games, team):

    win = games.filter(
        game_type=0,
        home_team_id=team.id,
        home_pts__gt=F('away_pts')).count() + \
        games.filter(
        game_type=0,
        away_team_id=team.id,
        away_pts__gt=F('home_pts')).count()

    loss = games.filter(
        game_type=0,
        home_team_id=team.id,
        home_pts__lt=F('away_pts')).count() + \
        games.filter(
        game_type=0,
        away_team_id=team.id,
        away_pts__lt=F('home_pts')).count()

    win_p = (Decimal(win)/Decimal(win+loss)).quantize(Decimal(10)**-3)

    return {
        'win': win,
        'loss': loss,
        'win_p': win_p,
    }

# Returns the pace (poss/regular game [48 for PBA, 40 otherwise])
# in a given set of games.


def get_pace(games, team=None):

    if team:
        league = League.objects.get(id=team.league.id)
        team_games = games.filter(
            home_team_id=team.id) | games.filter(
            away_team_id=team.id)

        team_game_stats = GameTeamStat.objects.filter(
            game_id__in=team_games.values_list('id', flat=True),
            team_id=team.id)

        opp_game_stats = GameTeamStat.objects.filter(
            game_id__in=team_games.values_list('id', flat=True)).exclude(
                team_id=team.id)

        team_orb_percent = (Decimal(team_game_stats.aggregate(Sum(
            'offensive_reb'))['offensive_reb__sum']) /
            (Decimal(team_game_stats.aggregate(Sum(
                'offensive_reb'))['offensive_reb__sum']) +
                Decimal(opp_game_stats.aggregate(Sum(
                    'defensive_reb'))['defensive_reb__sum'])))

        opp_orb_percent = (Decimal(opp_game_stats.aggregate(Sum(
            'offensive_reb'))['offensive_reb__sum']) /
            (Decimal(opp_game_stats.aggregate(Sum(
                'offensive_reb'))['offensive_reb__sum']) +
                Decimal(team_game_stats.aggregate(Sum(
                    'defensive_reb'))['defensive_reb__sum'])))

        team_poss = Decimal(team_game_stats.aggregate(Sum(
            'fg_attempts'))['fg_attempts__sum']) + \
            Decimal(team_game_stats.aggregate(Sum(
                'turnovers'))['turnovers__sum']) + \
            Decimal(0.44) * Decimal(team_game_stats.aggregate(Sum(
                'ft_attempts'))['ft_attempts__sum']) - \
            team_orb_percent * (Decimal(team_game_stats.aggregate(Sum(
                'fg_attempts'))['fg_attempts__sum']) -
                                Decimal(team_game_stats.aggregate(Sum(
                                    'fg_made'))['fg_made__sum']))

        opp_poss = Decimal(opp_game_stats.aggregate(Sum(
            'fg_attempts'))['fg_attempts__sum']) + \
            Decimal(opp_game_stats.aggregate(Sum(
                'turnovers'))['turnovers__sum']) + \
            Decimal(0.44) * Decimal(opp_game_stats.aggregate(Sum(
                'ft_attempts'))['ft_attempts__sum']) - \
            opp_orb_percent * (Decimal(opp_game_stats.aggregate(Sum(
                'fg_attempts'))['fg_attempts__sum']) -
                                Decimal(opp_game_stats.aggregate(Sum(
                                    'fg_made'))['fg_made__sum']))

        ave_poss = (team_poss + opp_poss)/2

        standard_league_seconds_played = Decimal(league.periods) * \
            Decimal(league.mins_per_period) * 60 * 5

        ave_seconds_played = (Decimal(team_game_stats.aggregate(
            Avg('seconds_played'))['seconds_played__avg']) +
            Decimal(team_game_stats.aggregate(
                Avg('seconds_played'))['seconds_played__avg'])) / 2

        return (ave_poss * (standard_league_seconds_played /
                ave_seconds_played) /
                team_game_stats.count()).quantize(Decimal(10)**-1)
    else:
        league = League.objects.get(
            id=games.values_list('league_id').distinct())
        game_stats = GameTeamStat.objects.filter(
            game_id__in=games.values_list('id', flat=True))

        orb_percent = (Decimal(game_stats.aggregate(Sum(
            'offensive_reb'))['offensive_reb__sum']) /
            (Decimal(game_stats.aggregate(Sum(
                'offensive_reb'))['offensive_reb__sum']) +
                Decimal(game_stats.aggregate(Sum(
                    'defensive_reb'))['defensive_reb__sum'])))

        poss = Decimal(game_stats.aggregate(Sum(
            'fg_attempts'))['fg_attempts__sum']) + \
            Decimal(game_stats.aggregate(Sum(
                'turnovers'))['turnovers__sum']) + \
            Decimal(0.44) * Decimal(game_stats.aggregate(Sum(
                'ft_attempts'))['ft_attempts__sum']) - \
            orb_percent * (Decimal(game_stats.aggregate(Sum(
                'fg_attempts'))['fg_attempts__sum']) -
                                Decimal(game_stats.aggregate(Sum(
                                    'fg_made'))['fg_made__sum']))

        standard_league_seconds_played = Decimal(league.periods) * \
            Decimal(league.mins_per_period) * 60 * 5 * \
            Decimal(game_stats.count())

        league_seconds_played = Decimal(
            game_stats.aggregate(Sum('seconds_played'))['seconds_played__sum'])

        return (poss * (standard_league_seconds_played /
                league_seconds_played) /
                game_stats.count()).quantize(Decimal(10)**-1)

# Returns a rating [off/def] of a team OR a league in a given set of games.


def get_eff_ratings(games, rating=None, team=None, decimal=1):
    if team:
        team_games = games.filter(
            home_team_id=team.id) | games.filter(
            away_team_id=team.id)

        team_game_stats = GameTeamStat.objects.filter(
            game_id__in=team_games.values_list('id', flat=True),
            team_id=team.id)

        opp_game_stats = GameTeamStat.objects.filter(
            game_id__in=team_games.values_list('id', flat=True)).exclude(
                team_id=team.id)

        team_orb_percent = (Decimal(team_game_stats.aggregate(Sum(
            'offensive_reb'))['offensive_reb__sum']) /
            (Decimal(team_game_stats.aggregate(Sum(
                'offensive_reb'))['offensive_reb__sum']) +
                Decimal(opp_game_stats.aggregate(Sum(
                    'defensive_reb'))['defensive_reb__sum'])))

        opp_orb_percent = (Decimal(opp_game_stats.aggregate(Sum(
            'offensive_reb'))['offensive_reb__sum']) /
            (Decimal(opp_game_stats.aggregate(Sum(
                'offensive_reb'))['offensive_reb__sum']) +
                Decimal(team_game_stats.aggregate(Sum(
                    'defensive_reb'))['defensive_reb__sum'])))

        team_poss = Decimal(team_game_stats.aggregate(Sum(
            'fg_attempts'))['fg_attempts__sum']) + \
            Decimal(team_game_stats.aggregate(Sum(
                'turnovers'))['turnovers__sum']) + \
            Decimal(0.44) * Decimal(team_game_stats.aggregate(Sum(
                'ft_attempts'))['ft_attempts__sum']) - \
            team_orb_percent * (Decimal(team_game_stats.aggregate(Sum(
                'fg_attempts'))['fg_attempts__sum']) -
                                Decimal(team_game_stats.aggregate(Sum(
                                    'fg_made'))['fg_made__sum']))

        opp_poss = Decimal(opp_game_stats.aggregate(Sum(
            'fg_attempts'))['fg_attempts__sum']) + \
            Decimal(opp_game_stats.aggregate(Sum(
                'turnovers'))['turnovers__sum']) + \
            Decimal(0.44) * Decimal(opp_game_stats.aggregate(Sum(
                'ft_attempts'))['ft_attempts__sum']) - \
            opp_orb_percent * (Decimal(opp_game_stats.aggregate(Sum(
                'fg_attempts'))['fg_attempts__sum']) -
                                Decimal(opp_game_stats.aggregate(Sum(
                                    'fg_made'))['fg_made__sum']))

        ave_poss = (team_poss + opp_poss)/2

        if rating == 'off':
            points = Decimal(team_game_stats.aggregate(
                Sum('ft_made'))['ft_made__sum']) + \
                Decimal(team_game_stats.aggregate(
                    Sum('fg_made'))['fg_made__sum']) * 2 + \
                Decimal(team_game_stats.aggregate(
                    Sum('three_pt_made'))['three_pt_made__sum'])

            return (100 * points / ave_poss).quantize(Decimal(10) ** -1)
        elif rating == 'def':
            points = Decimal(opp_game_stats.aggregate(
                Sum('ft_made'))['ft_made__sum']) + \
                Decimal(opp_game_stats.aggregate(
                    Sum('fg_made'))['fg_made__sum']) * 2 + \
                Decimal(opp_game_stats.aggregate(
                    Sum('three_pt_made'))['three_pt_made__sum'])

            return (100 * points / ave_poss).quantize(Decimal(10) ** -1)
    else:
        game_stats = GameTeamStat.objects.filter(
            game_id__in=games.values_list('id', flat=True))

        orb_percent = (Decimal(game_stats.aggregate(Sum(
            'offensive_reb'))['offensive_reb__sum']) /
            (Decimal(game_stats.aggregate(Sum(
                'offensive_reb'))['offensive_reb__sum']) +
                Decimal(game_stats.aggregate(Sum(
                    'defensive_reb'))['defensive_reb__sum'])))

        poss = Decimal(game_stats.aggregate(Sum(
            'fg_attempts'))['fg_attempts__sum']) + \
            Decimal(game_stats.aggregate(Sum(
                'turnovers'))['turnovers__sum']) + \
            Decimal(0.44) * Decimal(game_stats.aggregate(Sum(
                'ft_attempts'))['ft_attempts__sum']) - \
            orb_percent * (Decimal(game_stats.aggregate(Sum(
                'fg_attempts'))['fg_attempts__sum']) -
                                Decimal(game_stats.aggregate(Sum(
                                    'fg_made'))['fg_made__sum']))

        points = Decimal(game_stats.aggregate(
            Sum('ft_made'))['ft_made__sum']) + \
            Decimal(game_stats.aggregate(
                Sum('fg_made'))['fg_made__sum']) * 2 + \
            Decimal(game_stats.aggregate(
                Sum('three_pt_made'))['three_pt_made__sum'])

        return (100 * points / poss).quantize(Decimal(10) ** -decimal)

# returns a dict of totals for all stats


def get_stat(games):
    total_points_scored = Decimal(games.aggregate(
        Sum('ft_made'))['ft_made__sum']) + \
        Decimal(games.aggregate(
            Sum('fg_made'))['fg_made__sum']) * 2 + \
        Decimal(games.aggregate(
            Sum('three_pt_made'))['three_pt_made__sum'])

    total_fg_made = Decimal(games.aggregate(
        Sum('fg_made'))['fg_made__sum'])

    total_fg_attempts = Decimal(games.aggregate(
        Sum('fg_attempts'))['fg_attempts__sum'])

    if total_fg_attempts > 0:
        fg_percent = ((total_fg_made/total_fg_attempts) *
                      100).quantize(Decimal(10)**-1)
    else:
        fg_percent = Decimal(0.0).quantize(Decimal(10)**-1)

    total_three_pt_made = Decimal(games.aggregate(
        Sum('three_pt_made'))['three_pt_made__sum'])

    total_three_pt_attempts = Decimal(games.aggregate(
        Sum('three_pt_attempts'))['three_pt_attempts__sum'])

    if total_three_pt_attempts > 0:
        three_pt_percent = ((total_three_pt_made/total_three_pt_attempts) *
                            100).quantize(Decimal(10)**-1)
    else:
        three_pt_percent = Decimal(0.0).quantize(Decimal(10)**-1)

    total_ft_made = Decimal(games.aggregate(
        Sum('ft_made'))['ft_made__sum'])

    total_ft_attempts = Decimal(games.aggregate(
        Sum('ft_attempts'))['ft_attempts__sum'])

    if total_ft_attempts > 0:
        ft_percent = ((total_ft_made/total_ft_attempts) *
                      100).quantize(Decimal(10)**-1)
    else:
        ft_percent = Decimal(0.0).quantize(Decimal(10)**-1)

    total_offensive_reb = Decimal(games.aggregate(
        Sum('offensive_reb'))['offensive_reb__sum'])

    total_defensive_reb = Decimal(games.aggregate(
        Sum('defensive_reb'))['defensive_reb__sum'])

    total_assists = Decimal(games.aggregate(
        Sum('assists'))['assists__sum'])

    total_steals = Decimal(games.aggregate(
        Sum('steals'))['steals__sum'])

    total_blocks = Decimal(games.aggregate(
        Sum('blocks'))['blocks__sum'])

    total_turnovers = Decimal(games.aggregate(
        Sum('turnovers'))['turnovers__sum'])

    total_personal_fouls = Decimal(games.aggregate(
        Sum('personal_fouls'))['personal_fouls__sum'])

    return ({
        'total_points_scored': total_points_scored,
        'total_fg_made': total_fg_made,
        'total_fg_attempts': total_fg_attempts,
        'fg_percent': fg_percent,
        'total_three_pt_made': total_three_pt_made,
        'total_three_pt_attempts': total_three_pt_attempts,
        'three_pt_percent': three_pt_percent,
        'total_ft_made': total_ft_made,
        'total_ft_attempts': total_ft_attempts,
        'ft_percent': ft_percent,
        'total_offensive_reb': total_offensive_reb,
        'total_defensive_reb': total_defensive_reb,
        'total_assists': total_assists,
        'total_steals': total_steals,
        'total_blocks': total_blocks,
        'total_turnovers': total_turnovers,
        'total_personal_fouls': total_personal_fouls,
        })


def get_player_stat(games, player, table_type, game_type=0):
    league = get_object_or_404(
        League,
        id__in=games.values_list('league_id', flat=True).distinct())
    player_games = GamePlayerStat.objects.filter(
        player_id=player.id,
        game_id__in=games.filter(
            game_type=game_type).values_list('id', flat=True),
        seconds_played__gt=0)

    games_played = player_games.count()

    games_started = player_games.filter(started="True").count()

    try:
        total_minutes_played = (Decimal(player_games.aggregate(
            Sum('seconds_played'))['seconds_played__sum']) /
            60).quantize(Decimal(10)**-1)
    except TypeError:
        total_minutes_played = 0

    try:
        if league.id == 1:
            adjusted_minutes = 36 / total_minutes_played
        else:
            adjusted_minutes = 30 / total_minutes_played
    except ZeroDivisionError:
        adjusted_minutes = 1
    if total_minutes_played > 0:
        player_stat = get_stat(player_games)
    else:
        return ({
            'games_played': 0,
            'games_started': 0,
            'minutes_played': 0,
            'points_scored': 0,
            'fg_made': 0,
            'fg_attempts': 0,
            'fg_percent': 0,
            'three_pt_made': 0,
            'three_pt_attempts': 0,
            'three_pt_percent': 0,
            'ft_made': 0,
            'ft_attempts': 0,
            'ft_percent': 0,
            'offensive_reb': 0,
            'defensive_reb': 0,
            'reb': 0,
            'assists': 0,
            'steals': 0,
            'blocks': 0,
            'turnovers': 0,
            'personal_fouls': 0
            })
    if table_type == 'totals':
        return ({
            'games_played': games_played,
            'games_started': games_started,
            'minutes_played': total_minutes_played,
            'points_scored': player_stat['total_points_scored'],
            'fg_made': player_stat['total_fg_made'],
            'fg_attempts': player_stat['total_fg_attempts'],
            'fg_percent': player_stat['fg_percent'],
            'three_pt_made': player_stat['total_three_pt_made'],
            'three_pt_attempts': player_stat['total_three_pt_attempts'],
            'three_pt_percent': player_stat['three_pt_percent'],
            'ft_made': player_stat['total_ft_made'],
            'ft_attempts': player_stat['total_ft_attempts'],
            'ft_percent': player_stat['ft_percent'],
            'offensive_reb': player_stat['total_offensive_reb'],
            'defensive_reb': player_stat['total_defensive_reb'],
            'reb': player_stat['total_offensive_reb'] +
            player_stat['total_defensive_reb'],
            'assists': player_stat['total_assists'],
            'steals': player_stat['total_steals'],
            'blocks': player_stat['total_blocks'],
            'turnovers': player_stat['total_turnovers'],
            'personal_fouls': player_stat['total_personal_fouls']
            })

    elif table_type == 'per_game':
        return ({
            'games_played': games_played,
            'games_started': games_started,
            'minutes_played': (total_minutes_played /
                               Decimal(games_played)).quantize(
                               Decimal(10)**-1),
            'points_scored': (player_stat['total_points_scored'] /
                              Decimal(games_played)).quantize(
                              Decimal(10)**-1),
            'fg_made': (player_stat['total_fg_made'] /
                        Decimal(games_played)).quantize(
                        Decimal(10)**-1),
            'fg_attempts': (player_stat['total_fg_attempts'] /
                            Decimal(games_played)).quantize(
                            Decimal(10)**-1),
            'fg_percent': player_stat['fg_percent'],
            'three_pt_made': (player_stat['total_three_pt_made'] /
                              Decimal(games_played)).quantize(
                              Decimal(10)**-1),
            'three_pt_attempts': (player_stat['total_three_pt_attempts'] /
                                  Decimal(games_played)).quantize(
                                  Decimal(10)**-1),
            'three_pt_percent': player_stat['three_pt_percent'],
            'ft_made': (player_stat['total_ft_made'] /
                        Decimal(games_played)).quantize(
                        Decimal(10)**-1),
            'ft_attempts': (player_stat['total_ft_attempts'] /
                            Decimal(games_played)).quantize(
                            Decimal(10)**-1),
            'ft_percent': player_stat['ft_percent'],
            'offensive_reb': (player_stat['total_offensive_reb'] /
                              Decimal(games_played)).quantize(
                              Decimal(10)**-1),
            'defensive_reb': (player_stat['total_defensive_reb'] /
                              Decimal(games_played)).quantize(
                              Decimal(10)**-1),
            'reb': ((player_stat['total_offensive_reb'] +
                     player_stat['total_defensive_reb']) /
                    Decimal(games_played)).quantize(
                    Decimal(10)**-1),
            'assists': (player_stat['total_assists'] /
                                  Decimal(games_played)).quantize(
                                  Decimal(10)**-1),
            'steals': (player_stat['total_steals'] /
                       Decimal(games_played)).quantize(
                       Decimal(10)**-1),
            'blocks': (player_stat['total_blocks'] /
                       Decimal(games_played)).quantize(
                       Decimal(10)**-1),
            'turnovers': (player_stat['total_turnovers'] /
                          Decimal(games_played)).quantize(
                          Decimal(10)**-1),
            'personal_fouls': (player_stat['total_personal_fouls'] /
                               Decimal(games_played)).quantize(
                               Decimal(10)**-1)
            })

    elif table_type == 'per_three_six':
        return ({
            'games_played': games_played,
            'games_started': games_started,
            'minutes_played': (total_minutes_played /
                               Decimal(games_played)).quantize(
                               Decimal(10)**-1),
            'points_scored': (adjusted_minutes *
                              player_stat['total_points_scored']).quantize(
                Decimal(10)**-1),
            'fg_made': (adjusted_minutes *
                        player_stat['total_fg_made']).quantize(
                Decimal(10)**-1),
            'fg_attempts': (adjusted_minutes *
                            player_stat['total_fg_attempts']).quantize(
                Decimal(10)**-1),
            'fg_percent': player_stat['fg_percent'],
            'three_pt_made': (adjusted_minutes *
                              player_stat['total_three_pt_made']).quantize(
                Decimal(10)**-1),
            'three_pt_attempts': (adjusted_minutes *
                                  player_stat['total_three_pt_attempts']
                                  ).quantize(
                                  Decimal(10)**-1),
            'three_pt_percent': player_stat['three_pt_percent'],
            'ft_made': (adjusted_minutes * player_stat['total_ft_made']
                        ).quantize(Decimal(10)**-1),
            'ft_attempts': (adjusted_minutes * player_stat['total_ft_attempts']
                            ).quantize(Decimal(10)**-1),
            'ft_percent': player_stat['ft_percent'],
            'offensive_reb': (adjusted_minutes *
                              player_stat['total_offensive_reb']).quantize(
                              Decimal(10)**-1),
            'defensive_reb': (adjusted_minutes *
                              player_stat['total_defensive_reb']).quantize(
                              Decimal(10)**-1),
            'reb': (adjusted_minutes *
                    (player_stat['total_offensive_reb'] +
                        player_stat['total_defensive_reb'])).quantize(
                    Decimal(10)**-1),
            'assists': (adjusted_minutes * player_stat['total_assists']
                        ).quantize(Decimal(10)**-1),
            'steals': (adjusted_minutes * player_stat['total_steals']
                       ).quantize(Decimal(10)**-1),
            'blocks': (adjusted_minutes * player_stat['total_blocks']
                       ).quantize(Decimal(10)**-1),
            'turnovers': (adjusted_minutes *
                          player_stat['total_turnovers']
                          ).quantize(Decimal(10)**-1),
            'personal_fouls': (adjusted_minutes *
                               player_stat['total_personal_fouls']).quantize(
                               Decimal(10)**-1)
            })

    elif table_type == 'advanced':
        return ({
            'games_played': games_played,
            'games_started': games_started,
            'minutes_played': total_minutes_played,
            })
# 60 = seconds per minute
# 5 = 5 players on the court


def get_team_stat(games, team, table_type, team_type='team', game_type=0):
    team_games = GameTeamStat.objects.filter(
        team_id=team.id,
        game_id__in=games.filter(
            game_type=game_type).values_list('id', flat=True),
        seconds_played__gt=0)

    opp_team_games = GameTeamStat.objects.filter(
        opp_team_id=team.id,
        game_id__in=games.filter(
            game_type=game_type).values_list('id', flat=True),
        seconds_played__gt=0)

    games_played = team_games.count()

    team_total_minutes_played = (Decimal(team_games.aggregate(
        Sum('seconds_played'))['seconds_played__sum']) /
        60).quantize(Decimal(10)**-1)

    opp_team_total_minutes_played = (Decimal(opp_team_games.aggregate(
        Sum('seconds_played'))['seconds_played__sum']) /
        60).quantize(Decimal(10)**-1)

    team_stats = get_stat(team_games)
    opp_team_stats = get_stat(opp_team_games)

    team_total_reb = team_stats['total_offensive_reb'] + \
        team_stats['total_defensive_reb']

    opp_team_total_reb = opp_team_stats['total_offensive_reb'] + \
        opp_team_stats['total_defensive_reb']

    team_stats.update({
        'total_games_played': games_played,
        'total_minutes_played': team_total_minutes_played,
        'reb': team_total_reb,
        })

    opp_team_stats.update({
        'total_games_played': games_played,
        'total_minutes_played': opp_team_total_minutes_played,
        'reb': opp_team_total_reb,
        })

    if table_type == 'totals':
        if team_type == 'team':
            return team_stats
        else:
            return opp_team_stats

    elif table_type == 'per_game':
        if team_type == 'team':
            return ({
                'games_played': games_played,
                'minutes_played': (team_total_minutes_played /
                                   Decimal(games_played)).quantize(
                                   Decimal(10)**-1),
                'points_scored': (team_stats['total_points_scored'] /
                                  Decimal(games_played)).quantize(
                                  Decimal(10)**-1),
                'fg_made': (team_stats['total_fg_made'] /
                            Decimal(games_played)).quantize(
                            Decimal(10)**-1),
                'fg_attempts': (team_stats['total_fg_attempts'] /
                                Decimal(games_played)).quantize(
                                Decimal(10)**-1),
                'fg_percent': team_stats['fg_percent'],
                'three_pt_made': (team_stats['total_three_pt_made'] /
                                  Decimal(games_played)).quantize(
                                  Decimal(10)**-1),
                'three_pt_attempts': (team_stats['total_three_pt_attempts'] /
                                      Decimal(games_played)).quantize(
                                      Decimal(10)**-1),
                'three_pt_percent': team_stats['three_pt_percent'],
                'ft_made': (team_stats['total_ft_made'] /
                            Decimal(games_played)).quantize(
                            Decimal(10)**-1),
                'ft_attempts': (team_stats['total_ft_attempts'] /
                                Decimal(games_played)).quantize(
                                Decimal(10)**-1),
                'ft_percent': team_stats['ft_percent'],
                'offensive_reb': (team_stats['total_offensive_reb'] /
                                  Decimal(games_played)).quantize(
                                  Decimal(10)**-1),
                'defensive_reb': (team_stats['total_defensive_reb'] /
                                  Decimal(games_played)).quantize(
                                  Decimal(10)**-1),
                'reb': ((team_stats['total_offensive_reb'] +
                         team_stats['total_defensive_reb']) /
                        Decimal(games_played)).quantize(
                        Decimal(10)**-1),
                'assists': (team_stats['total_assists'] /
                                      Decimal(games_played)).quantize(
                                      Decimal(10)**-1),
                'steals': (team_stats['total_steals'] /
                           Decimal(games_played)).quantize(
                           Decimal(10)**-1),
                'blocks': (team_stats['total_blocks'] /
                           Decimal(games_played)).quantize(
                           Decimal(10)**-1),
                'turnovers': (team_stats['total_turnovers'] /
                              Decimal(games_played)).quantize(
                              Decimal(10)**-1),
                'personal_fouls': (team_stats['total_personal_fouls'] /
                                   Decimal(games_played)).quantize(
                                   Decimal(10)**-1)
                })
        else:
            return ({
                'games_played': games_played,
                'minutes_played': (opp_team_total_minutes_played /
                                   Decimal(games_played)).quantize(
                                   Decimal(10)**-1),
                'points_scored': (opp_team_stats['total_points_scored'] /
                                  Decimal(games_played)).quantize(
                                  Decimal(10)**-1),
                'fg_made': (opp_team_stats['total_fg_made'] /
                            Decimal(games_played)).quantize(
                            Decimal(10)**-1),
                'fg_attempts': (opp_team_stats['total_fg_attempts'] /
                                Decimal(games_played)).quantize(
                                Decimal(10)**-1),
                'fg_percent': opp_team_stats['fg_percent'],
                'three_pt_made': (opp_team_stats['total_three_pt_made'] /
                                  Decimal(games_played)).quantize(
                                  Decimal(10)**-1),
                'three_pt_attempts': (opp_team_stats[
                    'total_three_pt_attempts'] /
                                      Decimal(games_played)).quantize(
                                      Decimal(10)**-1),
                'three_pt_percent': opp_team_stats['three_pt_percent'],
                'ft_made': (opp_team_stats['total_ft_made'] /
                            Decimal(games_played)).quantize(
                            Decimal(10)**-1),
                'ft_attempts': (opp_team_stats['total_ft_attempts'] /
                                Decimal(games_played)).quantize(
                                Decimal(10)**-1),
                'ft_percent': opp_team_stats['ft_percent'],
                'offensive_reb': (opp_team_stats['total_offensive_reb'] /
                                  Decimal(games_played)).quantize(
                                  Decimal(10)**-1),
                'defensive_reb': (opp_team_stats['total_defensive_reb'] /
                                  Decimal(games_played)).quantize(
                                  Decimal(10)**-1),
                'reb': ((opp_team_stats['total_offensive_reb'] +
                         opp_team_stats['total_defensive_reb']) /
                        Decimal(games_played)).quantize(
                        Decimal(10)**-1),
                'assists': (opp_team_stats['total_assists'] /
                                      Decimal(games_played)).quantize(
                                      Decimal(10)**-1),
                'steals': (opp_team_stats['total_steals'] /
                           Decimal(games_played)).quantize(
                           Decimal(10)**-1),
                'blocks': (opp_team_stats['total_blocks'] /
                           Decimal(games_played)).quantize(
                           Decimal(10)**-1),
                'turnovers': (opp_team_stats['total_turnovers'] /
                              Decimal(games_played)).quantize(
                              Decimal(10)**-1),
                'personal_fouls': (opp_team_stats['total_personal_fouls'] /
                                   Decimal(games_played)).quantize(
                                   Decimal(10)**-1)
                })

    elif table_type == 'adv':
        ortg = get_eff_ratings(games.filter(game_type=0), 'off', team)
        drtg = get_eff_ratings(games.filter(game_type=0), 'def', team)

        o_efg = (100*((Decimal(team_stats['total_fg_made']) +
                      (Decimal(team_stats['total_three_pt_made'])/2)) /
                      Decimal(team_stats['total_fg_attempts']))).quantize(
                    Decimal(10)**-1)

        d_efg = (100*((Decimal(opp_team_stats['total_fg_made']) +
                      (Decimal(opp_team_stats['total_three_pt_made'])/2)) /
                      Decimal(opp_team_stats['total_fg_attempts']))).quantize(
                    Decimal(10)**-1)

        o_tov = (100*Decimal(team_stats['total_turnovers']) /
                 (Decimal(team_stats['total_fg_attempts']) +
                 (Decimal(0.44) * Decimal(team_stats['total_ft_attempts'])) +
                 Decimal(team_stats['total_turnovers']))).quantize(
                Decimal(10)**-1)

        d_tov = (100*Decimal(opp_team_stats['total_turnovers']) /
                 (Decimal(opp_team_stats['total_fg_attempts']) +
                 (Decimal(0.44) * Decimal(
                    opp_team_stats['total_ft_attempts'])) +
                 Decimal(opp_team_stats['total_turnovers']))).quantize(
                Decimal(10)**-1)

        o_orb = (100 * Decimal(team_stats['total_offensive_reb']) /
                 (Decimal(team_stats['total_offensive_reb']) +
                  Decimal(opp_team_stats['total_defensive_reb']))).quantize(
                Decimal(10)**-1)

        d_orb = (100 * Decimal(opp_team_stats['total_offensive_reb']) /
                 (Decimal(opp_team_stats['total_offensive_reb']) +
                  Decimal(team_stats['total_defensive_reb']))).quantize(
                Decimal(10)**-1)

        o_ftp = (100 * Decimal(team_stats['total_ft_made']) /
                 Decimal(team_stats['total_fg_attempts'])).quantize(
                 Decimal(10)**-1)

        d_ftp = (100 * Decimal(opp_team_stats['total_ft_made']) /
                 Decimal(opp_team_stats['total_fg_attempts'])).quantize(
                 Decimal(10)**-1)

        return ({
            'three_point_rate': (100*Decimal(team_stats[
                'total_three_pt_attempts']) /
                Decimal(team_stats['total_fg_attempts'])).quantize(
                Decimal(10)**-1),
            'ft_rate': (100*Decimal(team_stats[
                'total_ft_attempts']) /
                Decimal(team_stats['total_fg_attempts'])).quantize(
                Decimal(10)**-1),
            'o_efg': o_efg,
            'o_tov': o_tov,
            'o_orb': o_orb,
            'o_ftp': o_ftp,
            'd_efg': d_efg,
            'd_tov': d_tov,
            'd_orb': d_orb,
            'd_ftp': d_ftp,
            'diff_rtg': ortg - drtg,
            'diff_efg': o_efg - d_efg,
            'diff_tov': o_tov - d_tov,
            'diff_orb': o_orb - d_orb,
            'diff_ftp': o_ftp - d_ftp,
            })


def get_per(games, player, tournament, game_type=0):
    player_games = GamePlayerStat.objects.filter(
        player_id=player.id,
        game_id__in=games.filter(
            game_type=game_type).values_list('id', flat=True))

    league_tournament_games = Game.objects.filter(
        league_id=tournament.league.id,
        schedule__gte=tournament.start_date,
        schedule__lte=tournament.end_date)

    league_games = GameTeamStat.objects.filter(
        game_id__in=league_tournament_games.filter(
            game_type=game_type).values_list('id', flat=True),
        seconds_played__gt=0)

    team_games = league_games.filter(team_id=PlayerTournamentTeam.objects.get(
        tournament_id=tournament.id, player_id=player.id).team.id)

    player_stat = get_player_stat(games, player, 'totals')
    league_stat = get_stat(league_games)
    team_stat = get_stat(team_games)

    factor = (Decimal(2)/Decimal(3)) - \
             ((Decimal(league_stat['total_assists']) /
               Decimal(league_stat['total_fg_made'])) / 2) / \
        (2 * (Decimal(league_stat['total_fg_made']) /
         Decimal(league_stat['total_ft_made'])))

    VOP = get_eff_ratings(league_tournament_games) / 100

    DRB_P = Decimal(league_stat['total_defensive_reb']) / \
        (Decimal(league_stat['total_defensive_reb']) +
         Decimal(league_stat['total_offensive_reb']))

    player_uPER = (1/Decimal(player_stat['minutes_played'])) * \
                  (player_stat['three_pt_made'] +
                   (2 * player_stat['assists'] / 3) +
                   (2 - (factor * (Decimal(team_stat['total_assists']) /
                    Decimal(team_stat['total_fg_made'])))) * Decimal(
                    player_stat['fg_made']) +
                   player_stat['ft_made'] / 2 *
                   (1+(1-(Decimal(team_stat['total_assists']) /
                    Decimal(team_stat['total_fg_made']))) +
                    (2*(Decimal(team_stat['total_assists']) /
                     Decimal(team_stat['total_fg_made']))/3)) -
                   (VOP * player_stat['turnovers']) -
                   (VOP * DRB_P *
                    (Decimal(player_stat['fg_attempts']) -
                        Decimal(player_stat['fg_made']))) -
                   (VOP * (Decimal(44) / 100) * ((Decimal(44) / 100) +
                    ((Decimal(56) / 100) * DRB_P)) *
                    (Decimal(player_stat['ft_attempts']) -
                        Decimal(player_stat['ft_made']))) +
                   (VOP * (1-DRB_P) * Decimal(player_stat['defensive_reb'])) +
                   (VOP * DRB_P * Decimal(player_stat['offensive_reb'])) +
                   (VOP * Decimal(player_stat['steals'])) +
                   (VOP * DRB_P * Decimal(player_stat['blocks'])) -
                   (Decimal(player_stat['personal_fouls'])) *
                   ((Decimal(league_stat['total_ft_made']) /
                    Decimal(league_stat['total_personal_fouls'])) -
                   (Decimal(44)/100) * VOP *
                   (Decimal(league_stat['total_ft_made']) /
                    Decimal(league_stat['total_personal_fouls']))))

    return player_uPER
