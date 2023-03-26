from django.urls import path, include
import Session.views as views

urlpatterns = [
    path('chatroom/Admin', views.manage_chatroom),
    path('chatroom', views.join_chatroom),
    path('message/withdraw', views.withdraw_message),
    path('message', views.message)
]
