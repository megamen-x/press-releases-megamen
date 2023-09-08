from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class CustomUser(AbstractUser):
    pass


class Rating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    text = models.TextField()
    answer = models.CharField(max_length=250)


class KeyWords(models.Model):
    word = models.CharField(max_length=40)
    rating_id = models.ForeignKey(Rating, on_delete=models.CASCADE)


def user_initial_file_path(instance, filename):
    return 'user_{0}/initial/{1}'.format(instance.user.id, filename)

def user_predict_file_path(instance, filename):
    return 'user_{0}/predict/{1}'.format(instance.user.id, filename)


class RatingFile(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    file = models.FileField(upload_to=user_initial_file_path)
    corrected_file = models.FileField(upload_to=user_predict_file_path)