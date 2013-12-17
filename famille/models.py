# -*- coding=utf-8 -*-
from datetime import datetime

from django.contrib.auth.models import User
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateField(default=datetime.now)
    updated_at = models.DateField(default=datetime.now)

    class Meta:
        abstract = True


class UserInfo(BaseModel):
    """
    The common user info that a Famille and
    a Prestataire need.
    """
    user = models.OneToOneField(User)
    name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    surname = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)

    class Meta:
        abstract = True


class Famille(UserInfo):
    """
    The Famille user.
    """
    street = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=8)
    city = models.CharField(max_length=40)
    country = models.CharField(max_length=20, default="France")
    # TODO : planning
    # TODO : criteres


class Enfant(BaseModel):
    """
    An child of a Famille.
    """
    famille = models.ForeignKey(Famille)
    name = models.CharField(max_length=20)
    age = models.PositiveSmallIntegerField()


class Prestataire(UserInfo):
    """
    The Prestataire user.
    """
    type = models.CharField(max_length=40)
    sub_types = models.CharField(max_length=40)
