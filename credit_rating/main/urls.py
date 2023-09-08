from django.urls import path
from main.views import *
from . import views

urlpatterns = [
    path('', RatingView.as_view(), name='file'),
    path('mmtslider', slider, name='project-menu'),
    path('mmtmegamen', megamen, name='megamen-team-page'),
    path('404', page404, name='404'),
]