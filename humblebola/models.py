from __future__ import unicode_literals

from django.db import models

class League(models.Model):
	title = models.CharField(max_length=5)
	long_name = models.CharField(max_length=255)
	period = models.IntegerField()
	min_per_period = models.IntegerField()