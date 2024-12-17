from django.urls import path
from .views import *  # Import your view

urlpatterns = [
    path('result/', ScoreView.as_view(), name='score-result'),
]
