from django.db import models

# Create your models here.

class Event(models.Model):
	title = models.TextField()
	date = models.DateTimeField()
	dateEnd = models.DateTimeField()
	price = models.CharField(max_length=20)
	eventType = models.CharField(max_length=50)
	duration = models.CharField(max_length=50)
	description = models.TextField()
	url = models.URLField()
	likes = models.IntegerField()

class Intermediary(models.Model):
	username = models.CharField(max_length=20)
	eventID = models.IntegerField()
	date = models.DateTimeField()

class User(models.Model):
	name = models.CharField(max_length=20)
	title = models.CharField(max_length=50)
	description = models.TextField(null=True)
	colour = models.CharField(max_length=20)
	letterColour = models.CharField(max_length=20)
	fontSize = models.CharField(max_length=20)

class Update(models.Model):
	hour = models.DateTimeField()
