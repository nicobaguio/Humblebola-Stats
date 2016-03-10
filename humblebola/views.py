from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from .models import *
from datetime import date
# Create your views here.

def home_page(request, code):
    league = get_object_or_404(League, code = code)
    leagues = League.objects.all()
    return render(request, 'humblebola/home_page.html', {'league': league, 'leagues': leagues})

def schedule(request, code):
    league = get_object_or_404(League, code = code)
    games = Game.objects.filter(league_id=league.id)
    current_tournament = Tournament.objects.get(
        league_id=league.id,
        start_date__lt=date.today(),
        end_date__gt=date.today(),
        parent_id__gt=0)

    current_games = Game.objects.filter(
        league_id = league.id,
        schedule__gt=current_tournament.start_date,
        schedule__lt=current_tournament.end_date).order_by('schedule')

    return render(request, 'humblebola/schedule.html', {
        'league': league,
        'tournament': current_tournament,
        'games': current_games,
        'teams': Team.objects.all()})
