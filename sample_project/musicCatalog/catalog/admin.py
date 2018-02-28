from django.contrib import admin

# import models
from .models import (Genre, Artist, Album, Song, Favorite)


class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = list_display


class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name", "website", "instagram")
    search_fields = list_display


class AlbumAdmin(admin.ModelAdmin):
    list_display = ("name", "artist", "genre", "release_date")
    search_fields = list_display


class SongAdmin(admin.ModelAdmin):
    list_display = ("name", "album", "track", "duration")
    search_fields = list_display


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "song")
    search_fields = list_display


# Register your models here.
admin.site.register(Genre, GenreAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Song, SongAdmin)
admin.site.register(Favorite, FavoriteAdmin)
