from django.urls import path, include
import CSRF.views as views

urlpatterns = [
    path('get_token', views.getToken),
]
