from django.forms import ModelForm
from main.models import *


class RatingForm(ModelForm):
    class Meta:
        model = Rating
        fields = ['text']


class RatingFileForm(ModelForm):
    class Meta:
        model = RatingFile
        fields = ['file']