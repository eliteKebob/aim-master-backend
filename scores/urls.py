from django.urls import path
from .views import ScoreView

urlpatterns = [
    path('result/', ScoreView.as_view(), name='score-result'),
]
