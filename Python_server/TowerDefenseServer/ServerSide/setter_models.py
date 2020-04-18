from django.db import models

# Create your models here.


class Test(models.Model):
    name = models.CharField(max_length=5, default="game", editable=False)
    actual_build = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class User(models.Model):
    identity = models.CharField(max_length=127, unique=True)
    login = models.CharField(max_length=127, unique=True)
    password = models.CharField(max_length=127)
    public_key = models.CharField(max_length=127)
    private_key = models.CharField(max_length=127)
    game_build = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Player(models.Model):
    identity = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="user", unique=True)
    player_address = models.CharField(max_length=127, unique=True)
    user_address = models.CharField(max_length=127, unique=True)
    level = models.PositiveIntegerField()
    points = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class KeysRegister(models.Model):
    user_address = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name="player")
    public_key = models.CharField(max_length=127)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
