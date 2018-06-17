from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Recension(models.Model):
    text = models.CharField(max_length = 80000)
    #paper_set.all() za paper objekte koji se rencezurisu

class Paper(models.Model):
    title = models.CharField(max_length=100)
    Suggested='0'
    Revision='1'
    Rewriting='2'
    Refused='3'
    Accepted='4'
    Type_CHOICES = (
		(Suggested, 'Suggested'),
		(Revision, 'Revision'),
		(Rewriting, 'Rewriting'),
		(Refused, 'Refused'),
		(Accepted, 'Accepted'),
		)
    status = models.CharField(max_length=1,choices = Type_CHOICES)
    rec_total = models.SmallIntegerField()
    rec_completed = models.SmallIntegerField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="paper_author")
    reviewer = models.ManyToManyField(User, related_name="paper_reviewer")
    publisher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="paper_publilsher")
    deleted = models.BooleanField()
    recension = models.ManyToManyField(Recension)
    text = models.CharField(max_length = 80000)
    keywords = models.CharField(max_length = 300)
    paper_type = models.CharField(max_length = 100)
    class Meta:
        permissions = (("can_publish","Can supervise revision process"),("can_manage","Can change state of process for given article"),)

class Schema(models.Model):
    name = models.CharField(max_length=100, unique = True)
    text = models.CharField(max_length = 6000)

class Questionnaire(models.Model):
    text = models.CharField(max_length = 10000)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)