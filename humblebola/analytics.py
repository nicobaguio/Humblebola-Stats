from decimal import Decimal
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


def get_eff_ratings(games, rating=None, team=None):
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

        return (100 * points / poss).quantize(Decimal(10) ** -1)

# Return a dict of a player's totals/per game/per-36/adv in either
# regular or playoff games.


def get_player_stat(games, player, table_type, game_type=0):
    league = player.current_league
    player_games = GamePlayerStat.objects.filter(
        player_id=player.id,
        game_id__in=games.filter(
            game_type=game_type).values_list('id', flat=True),
        seconds_played__gt=0)

    games_played = player_games.count()

    games_started = player_games.filter(started="True").count()

    total_minutes_played = (Decimal(player_games.aggregate(
        Sum('seconds_played'))['seconds_played__sum']) /
        60).quantize(Decimal(10)**-1)

    if league.id == 1:
        adjusted_minutes = 36 / total_minutes_played
    else:
        adjusted_minutes = 30 / total_minutes_played

    total_points_scored = Decimal(player_games.aggregate(
        Sum('ft_made'))['ft_made__sum']) + \
        Decimal(player_games.aggregate(
            Sum('fg_made'))['fg_made__sum']) * 2 + \
        Decimal(player_games.aggregate(
            Sum('three_pt_made'))['three_pt_made__sum'])

    total_fg_made = Decimal(player_games.aggregate(
        Sum('fg_made'))['fg_made__sum'])

    total_fg_attempts = Decimal(player_games.aggregate(
        Sum('fg_attempts'))['fg_attempts__sum'])

    if total_fg_attempts > 0:
        fg_percent = ((total_fg_made/total_fg_attempts) *
                      100).quantize(Decimal(10)**-1)
    else:
        fg_percent = Decimal(0.0).quantize(Decimal(10)**-1)

    total_three_pt_made = Decimal(player_games.aggregate(
        Sum('three_pt_made'))['three_pt_made__sum'])

    total_three_pt_attempts = Decimal(player_games.aggregate(
        Sum('three_pt_attempts'))['three_pt_attempts__sum'])

    if total_three_pt_attempts > 0:
        three_pt_percent = ((total_three_pt_made/total_three_pt_attempts) *
                            100).quantize(Decimal(10)**-1)
    else:
        three_pt_percent = Decimal(0.0).quantize(Decimal(10)**-1)

    total_ft_made = Decimal(player_games.aggregate(
        Sum('ft_made'))['ft_made__sum'])

    total_ft_attempts = Decimal(player_games.aggregate(
        Sum('ft_attempts'))['ft_attempts__sum'])

    if total_ft_attempts > 0:
        ft_percent = ((total_ft_made/total_ft_attempts) *
                      100).quantize(Decimal(10)**-1)
    else:
        ft_percent = Decimal(0.0).quantize(Decimal(10)**-1)

    total_offensive_reb = Decimal(player_games.aggregate(
        Sum('offensive_reb'))['offensive_reb__sum'])

    total_defensive_reb = Decimal(player_games.aggregate(
        Sum('defensive_reb'))['defensive_reb__sum'])

    total_assists = Decimal(player_games.aggregate(
        Sum('assists'))['assists__sum'])

    total_steals = Decimal(player_games.aggregate(
        Sum('steals'))['steals__sum'])

    total_blocks = Decimal(player_games.aggregate(
        Sum('blocks'))['blocks__sum'])

    total_turnovers = Decimal(player_games.aggregate(
        Sum('turnovers'))['turnovers__sum'])

    total_personal_fouls = Decimal(player_games.aggregate(
        Sum('personal_fouls'))['personal_fouls__sum'])

    if table_type == 'totals':
        return ({
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
            'personal_fouls': total_personal_fouls
            })

    elif table_type == 'per_game':
        return ({
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
                              total_points_scored).quantize(
                Decimal(10)**-1),
            'fg_made': (adjusted_minutes * total_fg_made).quantize(
                Decimal(10)**-1),
            'fg_attempts': (adjusted_minutes * total_fg_attempts).quantize(
                Decimal(10)**-1),
            'fg_percent': fg_percent,
            'three_pt_made': (adjusted_minutes *
                              total_three_pt_made).quantize(
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
            'offensive_reb': (adjusted_minutes *
                              total_offensive_reb).quantize(
                              Decimal(10)**-1),
            'defensive_reb': (adjusted_minutes *
                              total_defensive_reb).quantize(
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
                               Decimal(10)**-1)
            })
# 60 = seconds per minute
# 5 = 5 players on the court
