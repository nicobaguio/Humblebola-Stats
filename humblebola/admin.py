from django.contrib import admin

# Register your models here.

from .models import *

class PlayerAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name')
    fields = (('last_name', 'first_name'),
                ('real_first_name', 'real_last_name'),
                 'current_jersey_number')

class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name' , 'start_date', 'end_date')
    fields = (('last_name', 'first_name'),
                ('real_first_name', 'real_last_name'),
                 'current_jersey_number')

admin.site.register(Player, PlayerAdmin)
admin.site.register(Tournament, TournamentAdmin)
admin.site.register(League)
