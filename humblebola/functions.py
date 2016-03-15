from decimal import Decimal
from django.db.models import F, Sum, Avg

from humblebola.models import *


def get_wins_losses(games, team):
    # Gets wins and losses for a team in the games
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


def get_pace(games, team=None):
    # Get pace for a given set of games and team
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


def team_get_ratings(games, rating=None, team=None):
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

# 60 = seconds per minute
# 5 = 5 players on the court
