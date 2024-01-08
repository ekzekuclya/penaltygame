from django.contrib import admin
from .models import Game, TelegramUser, Round, Result


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['id']


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username' if 'username' else 'None']


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ['id']


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['id']
