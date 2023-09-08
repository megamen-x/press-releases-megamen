from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class CustomUser(AbstractUser):
    pass


class Rating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    text = models.TextField()
    answer_detalized = models.CharField(max_length=10)
    answer_simplified = models.CharField(max_length=10)


class KeyWords(models.Model):
    construction = models.CharField(max_length=250)
    rating_id = models.ForeignKey(Rating, on_delete=models.CASCADE)


def user_file_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class InputFile(models.Model):
    
    class Formats(models.TextChoices):
        CSV = 'csv'
        XLSX = 'xlsx'
        TXT = "txt"

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    file = models.FileField(upload_to=user_file_path)
    output_format = models.CharField(max_length=4, choices=Formats.choices, default=Formats.CSV)