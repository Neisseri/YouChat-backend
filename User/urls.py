from django.urls import path, include
import User.views as views

urlpatterns = [
    path('user', views.user),
    path('friends/<query>', views.friends),
    path('friends', views.friends_put),
    path('email/send/<email>', views.email_send),
    path('email/verify/<v_code>', views.email_verify),
    path('profile/<id>', views.profile)
]
