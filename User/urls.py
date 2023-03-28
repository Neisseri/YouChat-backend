from django.urls import path, include
import User.views as views

urlpatterns = [
    path('user', views.user),
    path('friends/<query>', views.friends),
    path('modify/email', views.modify_email),
    path('email/send/<email>', views.email_send),
    path('email/verify', views.email_verify),
    path('profile/<id>', views.profile)
]
