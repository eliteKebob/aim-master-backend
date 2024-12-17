from django.db import models
from utils.dt import now_tz_offset

class Score(models.Model):
    class Modes(models.TextChoices):
        CHALLENGE = 'C', 'Challenge'
        CHILL = 'CH', 'Chill'

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    date = models.DateTimeField(default=now_tz_offset(3))
    game_length = models.IntegerField(default=30, help_text="Seconds per single game/session")
    target_size = models.IntegerField(default=3, help_text="Target size")
    total_target = models.IntegerField(default=7, help_text="Total targets on screen")
    target_hit = models.IntegerField(default=0, help_text="Total target hit")
    mode = models.CharField(max_length=2, choices=Modes.choices, default=Modes.CHILL)

