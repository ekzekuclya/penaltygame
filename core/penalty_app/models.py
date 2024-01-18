from django.db import models
from django.utils import timezone


class TelegramUser(models.Model):
    user_id = models.IntegerField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_super_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username if self.username else "None"


class Game(models.Model):
    date_started = models.DateTimeField(auto_now_add=True)
    players = models.ManyToManyField(TelegramUser, blank=True)
    over = models.BooleanField(default=False)
    chat_id = models.CharField(max_length=2555)
    message_id = models.CharField(max_length=2555, null=True)
    state = models.CharField(max_length=255, default="collecting")
    created_time = models.DateTimeField(default=timezone.now())
    waiting_time2 = models.IntegerField(default=10)
    owner = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, null=True, blank=True, related_name='owner')


class Round(models.Model):
    user1 = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, null=True, blank=True, related_name='user1')
    user2 = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, null=True, blank=True, related_name='user2')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True)
    user1_choice = models.PositiveIntegerField(null=True, blank=True)
    user2_choice = models.PositiveIntegerField(null=True, blank=True)
    chat_id = models.CharField(max_length=2555)
    message_id = models.CharField(max_length=2555, null=True)
    waiting_time2 = models.IntegerField(default=12)
    moved = models.BooleanField(default=False)


class Result(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True, related_name='result_game')
    player = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, null=True, blank=True, related_name='result_player')
    position = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['position']


class Chat(models.Model):
    chat_id = models.CharField(max_length=2555)
    len_users = models.PositiveIntegerField()
