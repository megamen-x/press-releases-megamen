from django.forms import ModelForm
from main.models import *


class RatingForm(ModelForm):
    class Meta:
        model = InputFile
        fields = ['file', 'output_format']