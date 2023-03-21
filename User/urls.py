from django.urls import path, include
import User.views as views

urlpatterns = [
    path('user', views.user),
    path('friends', views.friends),
    path('email/send', views.email_send),
    path('email/verify', views.email_verify)
]
