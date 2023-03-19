from django.urls import path, include
import User.views as views

urlpatterns = [
    path('user', views.user),
    path('friends', views.friends),
]
