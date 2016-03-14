from decimal import Decimal
from django.db.models import F


def get_wins_losses(games, team):
    #Gets wins and losses for a team in the games
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
