from django.urls import path, include
import User.views as views

urlpatterns = [
    path('/user', views.user),
    path('/friends', views.friends),
    path('/email/send/<email>', views.email_send),
    path('/email/verify/<v_code>', views.email_verify)
]
