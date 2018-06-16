from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError

from paper.views import Schema


def startup():
    groupA, created = Group.objects.get_or_create(name='author')
    if (created):
        groupA.permissions.clear()
        permission = Permission.objects.get(codename='add_paper')
        groupA.permissions.add(permission)
    groupR, created = Group.objects.get_or_create(name='reviewer')
    if (created):
        groupR.permissions.clear()
        permission = Permission.objects.get(codename='add_recension')
        groupR.permissions.add(permission)
    groupP, created = Group.objects.get_or_create(name='publisher')
    if (created):
        groupP.permissions.clear()
        permission = Permission.objects.get(codename='can_publish')
        groupP.permissions.add(permission)
        permission = Permission.objects.get(codename='can_manage')
        groupP.permissions.add(permission)
    #adding users
    try:
        user = User.objects.create_user(
            "author1", "djordjeilic55@gmail.com", "nottoocomplex",first_name="Auth1",last_name="Einz")
        user.groups.add(groupA)
        user.groups.add(groupR)
        user.save()
    except IntegrityError:
        pass
    try:
        user = User.objects.create_user(
            "author2", "djordjeilic55@gmail.com", "nottoocomplex",first_name="Auth2",last_name="Mark")
        user.groups.add(groupA)
        user.groups.add(groupR)
        user.save()
    except IntegrityError:
        pass
    try:
        user = User.objects.create_user(
            "author3", "djordjeilic55@gmail.com", "nottoocomplex",first_name="Auth3",last_name="Eliot")
        user.groups.add(groupA)
        user.groups.add(groupR)
        user.save()
    except IntegrityError:
        pass
    try:
        user = User.objects.create_user(
            "publisher1", "djordjeilic55@gmail.com", "nottoocomplex",first_name="Pub1",last_name="Novo")
        user.groups.add(groupP)
        user.groups.add(groupR)
        user.save()
    except IntegrityError:
        pass
    try:
        user = User.objects.create_user(
            "publisher2", "djordjeilic55@gmail.com", "nottoocomplex",first_name="Pub2",last_name="Old")
        user.groups.add(groupP)
        user.groups.add(groupR)
        user.save()
    except IntegrityError:
        pass
    try:
        schema = Schema()
        schema.name = "paper"
        fileS = open("../xmlschema/articleXML.xsd", 'r')
        schema.text = ''.join(fileS.readlines()[1:])
        fileS.close()
        schema.save()
    except IntegrityError:
        pass
    try:
        schema = Schema()
        schema.name = "revision"
        fileS = open("../xmlschema/revisionXML.xsd", 'r')
        schema.text = ''.join(fileS.readlines()[1:])
        fileS.close()
        schema.save()
    except IntegrityError:
        pass
    try:
        schema = Schema()
        schema.name = "letter"
        fileS = open("../xmlschema/letterXML.xsd", 'r')
        schema.text = ''.join(fileS.readlines()[1:])
        fileS.close()
        schema.save()
    except IntegrityError:
        pass
    try:
        schema = Schema()
        schema.name = "questionnaire"
        fileS = open("../xmlschema/revisionQuestionaireXML.xsd", 'r')
        schema.text = ''.join(fileS.readlines()[1:])
        fileS.close()
        schema.save()
    except IntegrityError:
        pass
