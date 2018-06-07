from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError

def startup():
    groupA, created = Group.objects.get_or_create(name='author')
    if (created):
        groupA.permissions.clear()
        permission = Permission.objects.get(codename='get_alarms')
    groupR, created = Group.objects.get_or_create(name='reviewer')
    if (created):
        groupR.permissions.clear()
        permission = Permission.objects.get(codename='get_alarms')
        groupR.permissions.add(permission)
    groupP, created = Group.objects.get_or_create(name='publisher')
    if (created):
        groupP.permissions.clear()
        permission = Permission.objects.get(codename='get_alarms')
    #adding users
    try:
        user = User.objects.create_user("author1", "needtocreatenewemailforthis@gmail.com", "nottoocomplex")
        user.groups.add(groupA)
        user.groups.add(groupR)
        user.save()
    except IntegrityError:
        pass
    try:
        user = User.objects.create_user("author2", "needtocreatenewemailforthis@gmail.com", "nottoocomplex")
        user.groups.add(groupA)
        user.groups.add(groupR)
        user.save()
    except IntegrityError:
        pass
    try:
        user = User.objects.create_user("author3", "needtocreatenewemailforthis@gmail.com", "nottoocomplex")
        user.groups.add(groupA)
        user.groups.add(groupR)
        user.save()
    except IntegrityError:
        pass
    try:
        user = User.objects.create_user("publisher1", "needtocreatenewemailforthis@gmail.com", "nottoocomplex")
        user.groups.add(groupP)
        user.groups.add(groupR)
        user.save()
    except IntegrityError:
        pass
    try:
        user = User.objects.create_user("publisher2", "needtocreatenewemailforthis@gmail.com", "nottoocomplex")
        user.groups.add(groupP)
        user.groups.add(groupR)
        user.save()
    except IntegrityError:
        pass