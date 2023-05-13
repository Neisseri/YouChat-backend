from django.urls import path
import Session.views as views

urlpatterns = [
    path('chatroom/Admin', views.manage_chatroom),
    path('chatroom', views.join_chatroom),
    path('message/translate', views.message_translate),
    path('message/<id>', views.message),
    path('setting', views.setting),
    path('image', views.image),
    path('delete', views.delete),
    path('history', views.history),
]
