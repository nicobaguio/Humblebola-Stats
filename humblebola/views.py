from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from .models import *
# Create your views here.

def home_page(request, short_name):
    league = get_object_or_404(Leagues, short_name = short_name.upper())
    leagues = Leagues.objects.all()
    return render(request, 'humblebola/home_page.html', {'league': league, 'leagues': leagues})
