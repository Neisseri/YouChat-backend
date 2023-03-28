from django.urls import path, include
import User.views as views

urlpatterns = [
    path('user', views.user),
    path('friends/<query>', views.friends),
    path('modify/email', views.modify_email),
    path('email/send/<email>', views.email_send),
<<<<<<< HEAD
    path('email/verify', views.email_verify),
    path('profile/<id>', views.profile)
=======
    path('email/verify/<v_code>', views.email_verify),
    path('profile/<id>', views.profile),
    path('modify/email', views.modify_email),
    path('modify', views.modify)
>>>>>>> e64a71b093b215c37a63e8be121c20c0f78fec5f
]
