from django.db import models
from django.contrib.auth.models import User

class DetectionHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=150)
    followers = models.IntegerField()
    following = models.IntegerField()
    posts = models.IntegerField()
    bio_length = models.IntegerField()
    profile_pic = models.IntegerField()
    account_age_days = models.IntegerField()
    engagement_ratio = models.FloatField()
    result = models.CharField(max_length=20)  # 'FAKE' or 'GENUINE'
    detected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.result} at {self.detected_at}'

