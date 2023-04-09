from django.urls import path
import Session.views as views

urlpatterns = [
    path('chatroom/Admin', views.manage_chatroom),
    path('chatroom', views.join_chatroom),
    path('image/<user_id>', views.transmit_img)
]
