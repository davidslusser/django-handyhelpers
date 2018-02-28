from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# import HandyHelpers
from handyhelpers.managers import HandyHelperModelManager


class Genre(models.Model):
    """ Music Genres """
    objects = HandyHelperModelManager()
    name = models.CharField(max_length=32, help_text="name of contact")
    description = models.CharField(max_length=255, blank=True, null=True, help_text="describe this genre")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'genres'


class Artist(models.Model):
    """ Artist """
    objects = HandyHelperModelManager()
    name = models.CharField(max_length=32, blank=True, null=True, help_text="name of artist")
    website = models.URLField(blank=True, null=True, help_text="artists website")
    instagram = models.CharField(max_length=32, blank=True, null=True, help_text="Instagram handle")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'artists'


class Album(models.Model):
    """ Album """
    objects = HandyHelperModelManager()
    name = models.CharField(max_length=32, blank=True, null=True, help_text="album name")
    artist = models.ForeignKey(Artist, help_text="artist for this album")
    genre = models.ForeignKey(Genre, help_text="genre for this album")
    release_date = models.DateField(auto_now=True, help_text="date this album was released")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'albums'


class Song(models.Model):
    """ Song on an album """
    objects = HandyHelperModelManager()
    name = models.CharField(max_length=32, blank=True, null=True, help_text="name of song")
    album = models.ForeignKey(Album, help_text="album this song is on")
    track = models.IntegerField(help_text="tack number on album")
    duration = models.CharField(max_length=32, blank=True, null=True, help_text="length of song")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'songs'


class Favorite(models.Model):
    """ Track favorite songs """
    objects = HandyHelperModelManager()
    user = models.ForeignKey(User)
    song = models.ForeignKey(Song)

    class Meta:
        db_table = 'favorites'
