from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('prediction-result/', views.prediction_result, name='prediction_result'),
    #path('dashboard/', views.dash, name='dash'),
    path('account/', views.acc, name='acc'),
    #path('medical-history/', views.medical, name='medical'),
    path('log/', views.logout_view, name='log'),
]