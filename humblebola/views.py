from django.shortcuts import get_object_or_404, render

from .models import *
from datetime import date, datetime, time
# Create your views here.


def home_page(request, code):
    league = get_object_or_404(League, code=code)
    return render(request, 'humblebola/home_page.html', {'league': league})


def schedule(request, code):
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

    return render(request, 'humblebola/schedule.html', {
        'league': league,
        'tournament': current_tournament,
        'next_game': next_game,
        'prev_game': prev_game,
        'regular_games': current_games.filter(game_type=0),
        'playoff_games': current_games.filter(game_type=1),
        'teams': Team.objects.all()})
