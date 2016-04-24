 # This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = True` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class ArchivedTeamNames(models.Model):
    team_id = models.ForeignKey('Teams')
    code = models.CharField(max_length=255, blank=True, null=True)
    team_name = models.CharField(max_length=255, blank=True, null=True)
    nickname = models.CharField(max_length=255, blank=True, null=True)
    logo = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'archived_team_names'


class FibaGameInfos(models.Model):
    game_id = models.ForeignKey('Games')
    fiba_url = models.CharField(max_length=255, blank=True, null=True)
    fiba_id = models.IntegerField(blank=True, null=True)
    data_json = models.TextField(blank=True, null=True)
    home_team_number = models.IntegerField(blank=True, null=True)
    away_team_number = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'fiba_game_infos'


class FibaGamePlayers(models.Model):
    game_id = models.ForeignKey('Games')
    team_number = models.IntegerField(blank=True, null=True)
    player_number = models.IntegerField(blank=True, null=True)
    jersey_number = models.IntegerField(blank=True, null=True)
    player_name = models.CharField(max_length=255, blank=True, null=True)
    player_id = models.ForeignKey('Players')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'fiba_game_players'


class GameEvents(models.Model):
    game_id = models.ForeignKey('Games')
    team_id = models.ForeignKey('Teams', related_name="team_game_event")
    opp_team_id = models.ForeignKey('Teams', related_name='opp_game_event')
    player_id = models.ForeignKey('Players')
    period = models.IntegerField(blank=True, null=True)
    secs_remaining = models.IntegerField(blank=True, null=True)
    action_type = models.CharField(max_length=255, blank=True, null=True)
    action_subtype = models.CharField(max_length=255, blank=True, null=True)
    scoring = models.NullBooleanField()
    success = models.NullBooleanField()
    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)
    lineup = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = True
        db_table = 'game_events'


class GamePeriodScorings(models.Model):
    game_id = models.ForeignKey('Games')
    period = models.IntegerField(blank=True, null=True)
    home_pts = models.IntegerField(blank=True, null=True)
    away_pts = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'game_period_scorings'


class GamePlayerStats(models.Model):
    game_id = models.ForeignKey('Games')
    team_id = models.ForeignKey('Teams')
    player_id = models.ForeignKey('Players')
    player_jersey_number = models.IntegerField(blank=True, null=True)
    seconds_played = models.IntegerField(blank=True, null=True)
    fg_made = models.IntegerField(blank=True, null=True)
    fg_attempts = models.IntegerField(blank=True, null=True)
    three_pt_made = models.IntegerField(blank=True, null=True)
    three_pt_attempts = models.IntegerField(blank=True, null=True)
    ft_made = models.IntegerField(blank=True, null=True)
    ft_attempts = models.IntegerField(blank=True, null=True)
    offensive_reb = models.IntegerField(blank=True, null=True)
    defensive_reb = models.IntegerField(blank=True, null=True)
    assists = models.IntegerField(blank=True, null=True)
    steals = models.IntegerField(blank=True, null=True)
    blocks = models.IntegerField(blank=True, null=True)
    turnovers = models.IntegerField(blank=True, null=True)
    personal_fouls = models.IntegerField(blank=True, null=True)
    pts = models.IntegerField(blank=True, null=True)
    started = models.NullBooleanField()
    my_team_stat_id = models.ForeignKey('self', related_name="team_game_player_stat")
    opp_team_stat_id = models.ForeignKey('self', related_name="opp_game_player_stat")

    class Meta:
        managed = True
        db_table = 'game_player_stats'


class GameTeamStats(models.Model):
    game_id = models.ForeignKey('Games')
    team_id = models.ForeignKey('Teams', related_name="team_game_team_stat")
    opp_team_stat_id = models.ForeignKey('self')
    opp_team_id = models.ForeignKey('Teams', related_name="opp_game_team_stat")

    seconds_played = models.IntegerField(blank=True, null=True)
    fg_made = models.IntegerField(blank=True, null=True)
    fg_attempts = models.IntegerField(blank=True, null=True)
    three_pt_made = models.IntegerField(blank=True, null=True)
    three_pt_attempts = models.IntegerField(blank=True, null=True)
    ft_made = models.IntegerField(blank=True, null=True)
    ft_attempts = models.IntegerField(blank=True, null=True)
    offensive_reb = models.IntegerField(blank=True, null=True)
    defensive_reb = models.IntegerField(blank=True, null=True)
    assists = models.IntegerField(blank=True, null=True)
    steals = models.IntegerField(blank=True, null=True)
    blocks = models.IntegerField(blank=True, null=True)
    turnovers = models.IntegerField(blank=True, null=True)
    personal_fouls = models.IntegerField(blank=True, null=True)
    pts = models.IntegerField(blank=True, null=True)
    fastbreak_pts = models.IntegerField(blank=True, null=True)
    fastbreak_attempts = models.IntegerField(blank=True, null=True)
    second_chance_pts = models.IntegerField(blank=True, null=True)
    turnover_pts = models.IntegerField(blank=True, null=True)
    team_offensive_reb = models.IntegerField(blank=True, null=True)
    team_defensive_reb = models.IntegerField(blank=True, null=True)
    team_turnovers = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'game_team_stats'


class Games(models.Model):
    league_id = models.ForeignKey('Leagues')
    schedule = models.DateTimeField(blank=True, null=True)
    game_type = models.IntegerField(blank=True, null=True)
    home_team_id = models.ForeignKey('Teams', related_name='home_game')
    away_team_id = models.ForeignKey('Teams', related_name='away_game')
    home_pts = models.IntegerField(blank=True, null=True)
    away_pts = models.IntegerField(blank=True, null=True)
    periods = models.IntegerField(blank=True, null=True)
    pre_game_article_url = models.CharField(max_length=255, blank=True, null=True)
    post_game_article_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'games'


class Leagues(models.Model):
    code = models.CharField(max_length=255, blank=True, null=True)
    short_name = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    sort = models.IntegerField(blank=True, null=True)
    periods = models.IntegerField(blank=True, null=True)
    mins_per_period = models.IntegerField(blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'leagues'


class PlayerLeagues(models.Model):
    player_id = models.ForeignKey('Players')
    league_id = models.ForeignKey('Leagues')

    class Meta:
        managed = True
        db_table = 'player_leagues'
        unique_together = (('player_id', 'league_id'),)


class PlayerTournamentTeams(models.Model):
    player_id = models.ForeignKey('Players')
    tournament_id = models.ForeignKey('Tournaments')
    team_id = models.ForeignKey('Teams')

    class Meta:
        managed = True
        db_table = 'player_tournament_teams'
        unique_together = (('player_id', 'team_id', 'tournament_id'),)


class Players(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    current_league_id = models.ForeignKey('Leagues')
    current_team_id = models.ForeignKey('Teams')
    current_jersey_number = models.IntegerField(blank=True, null=True)
    player_type = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    photo = models.CharField(max_length=255, blank=True, null=True)
    twitter = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    birth_place = models.CharField(max_length=255, blank=True, null=True)
    drafted = models.CharField(max_length=255, blank=True, null=True)
    highschool = models.CharField(max_length=255, blank=True, null=True)
    college = models.CharField(max_length=255, blank=True, null=True)
    nickname = models.CharField(max_length=255, blank=True, null=True)
    real_first_name = models.CharField(max_length=255, blank=True, null=True)
    real_last_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'players'


class SchemaMigrations(models.Model):
    version = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = True
        db_table = 'schema_migrations'


class Teams(models.Model):
    league_id = models.ForeignKey('Leagues')
    code = models.CharField(unique=True, max_length=255, blank=True, null=True)
    team_name = models.CharField(max_length=255, blank=True, null=True)
    nickname = models.CharField(max_length=255, blank=True, null=True)
    logo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'teams'


class Tournaments(models.Model):
    parent_id = models.ForeignKey('Tournaments')
    league_id = models.ForeignKey('Leagues')
    name = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    sub_tournaments_count = models.IntegerField(blank=True, null=True)
    short_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'tournaments'


class Users(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(unique=True, max_length=255)
    encrypted_password = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    reset_password_token = models.CharField(unique=True, max_length=255, blank=True, null=True)
    reset_password_sent_at = models.DateTimeField(blank=True, null=True)
    remember_created_at = models.DateTimeField(blank=True, null=True)
    sign_in_count = models.IntegerField()
    current_sign_in_at = models.DateTimeField(blank=True, null=True)
    last_sign_in_at = models.DateTimeField(blank=True, null=True)
    current_sign_in_ip = models.GenericIPAddressField(blank=True, null=True)
    last_sign_in_ip = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'users'


class Videos(models.Model):
    league_id = models.ForeignKey('Leagues')
    date = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    page_url = models.CharField(max_length=255, blank=True, null=True)
    video_url = models.CharField(max_length=255, blank=True, null=True)
    file = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'videos'
