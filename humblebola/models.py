# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models

__all__ = [
    "ArchivedTeamNames", "AuthGroup", "AuthGroupPermissions", "AuthPermission",
    "AuthUser", "AuthUserGroups", "AuthUserUserPermissions", "DjangoAdminLog",
    "DjangoContentType", "DjangoMigrations", "DjangoSession", "FibaGameInfos",
    "FibaGamePlayers", "GameEvents", "GamePeriodScorings", "GamePlayerStats",
    "GameTeamStats", "Games", "Leagues", "PlayerLeagues",
    "PlayerTournamentTeams", "Players", "SchemaMigrations", "Teams",
    "Tournaments", "Users", "Videos"]


class ArchivedTeamNames(models.Model):
    team_id = models.IntegerField(blank=True, null=True)
    code = models.CharField(max_length=255, blank=True, null=True)
    team_name = models.CharField(max_length=255, blank=True, null=True)
    nickname = models.CharField(max_length=255, blank=True, null=True)
    logo = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'archived_team_names'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class FibaGameInfos(models.Model):
    game_id = models.IntegerField(blank=True, null=True)
    fiba_url = models.CharField(max_length=255, blank=True, null=True)
    fiba_id = models.IntegerField(blank=True, null=True)
    data_json = models.TextField(blank=True, null=True)
    home_team_number = models.IntegerField(blank=True, null=True)
    away_team_number = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fiba_game_infos'


class FibaGamePlayers(models.Model):
    game_id = models.IntegerField(blank=True, null=True)
    team_number = models.IntegerField(blank=True, null=True)
    player_number = models.IntegerField(blank=True, null=True)
    jersey_number = models.IntegerField(blank=True, null=True)
    player_name = models.CharField(max_length=255, blank=True, null=True)
    player_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fiba_game_players'


class GameEvents(models.Model):
    game_id = models.IntegerField(blank=True, null=True)
    team_id = models.IntegerField(blank=True, null=True)
    opp_team_id = models.IntegerField(blank=True, null=True)
    player_id = models.IntegerField(blank=True, null=True)
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
        managed = False
        db_table = 'game_events'


class GamePeriodScorings(models.Model):
    game_id = models.IntegerField(blank=True, null=True)
    period = models.IntegerField(blank=True, null=True)
    home_pts = models.IntegerField(blank=True, null=True)
    away_pts = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'game_period_scorings'


class GamePlayerStats(models.Model):
    game_id = models.IntegerField(blank=True, null=True)
    team_id = models.IntegerField(blank=True, null=True)
    player_id = models.IntegerField(blank=True, null=True)
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
    my_team_stat_id = models.IntegerField(blank=True, null=True)
    opp_team_stat_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'game_player_stats'


class GameTeamStats(models.Model):
    game_id = models.IntegerField(blank=True, null=True)
    team_id = models.IntegerField(blank=True, null=True)
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
    opp_team_stat_id = models.IntegerField(blank=True, null=True)
    opp_team_id = models.IntegerField(blank=True, null=True)
    fastbreak_pts = models.IntegerField(blank=True, null=True)
    fastbreak_attempts = models.IntegerField(blank=True, null=True)
    second_chance_pts = models.IntegerField(blank=True, null=True)
    turnover_pts = models.IntegerField(blank=True, null=True)
    team_offensive_reb = models.IntegerField(blank=True, null=True)
    team_defensive_reb = models.IntegerField(blank=True, null=True)
    team_turnovers = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'game_team_stats'


class Games(models.Model):
    league_id = models.IntegerField(blank=True, null=True)
    schedule = models.DateTimeField(blank=True, null=True)
    game_type = models.IntegerField(blank=True, null=True)
    home_team_id = models.IntegerField(blank=True, null=True)
    away_team_id = models.IntegerField(blank=True, null=True)
    home_pts = models.IntegerField(blank=True, null=True)
    away_pts = models.IntegerField(blank=True, null=True)
    periods = models.IntegerField(blank=True, null=True)
    pre_game_article_url = models.CharField(max_length=255, blank=True, null=True)
    post_game_article_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
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
        managed = False
        db_table = 'leagues'


class PlayerLeagues(models.Model):
    player_id = models.IntegerField()
    league_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'player_leagues'
        unique_together = (('player_id', 'league_id'),)


class PlayerTournamentTeams(models.Model):
    player_id = models.IntegerField(blank=True, null=True)
    tournament_id = models.IntegerField(blank=True, null=True)
    team_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'player_tournament_teams'
        unique_together = (('player_id', 'team_id', 'tournament_id'),)


class Players(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    current_league_id = models.IntegerField(blank=True, null=True)
    current_team_id = models.IntegerField(blank=True, null=True)
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
        verbose_name = "Player"
        managed = False
        db_table = 'players'


class SchemaMigrations(models.Model):
    version = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'schema_migrations'


class Teams(models.Model):
    league_id = models.IntegerField(blank=True, null=True)
    code = models.CharField(unique=True, max_length=255, blank=True, null=True)
    team_name = models.CharField(max_length=255, blank=True, null=True)
    nickname = models.CharField(max_length=255, blank=True, null=True)
    logo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'teams'


class Tournaments(models.Model):
    parent_id = models.IntegerField(blank=True, null=True)
    league_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    sub_tournaments_count = models.IntegerField(blank=True, null=True)
    short_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
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
        managed = False
        db_table = 'users'


class Videos(models.Model):
    league_id = models.IntegerField(blank=True, null=True)
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
        managed = False
        db_table = 'videos'
