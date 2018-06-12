from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Recension(models.Model):
    pass
    #reviewer = models.OneToOneField(User,on_delete=models.CASCADE)
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
    author = models.OneToOneField(User, on_delete=models.CASCADE)
    reviewer = models.ManyToManyField(User)
    publisher = models.OneToOneField(User, on_delete=models.CASCADE)
    deleted = models.BooleanField()
    recension = models.ManyToManyField(Recension)
    location = models.CharField(max_length=200)
