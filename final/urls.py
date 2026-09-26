# chat/urls.py
from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_room, name="create_room"),
    path("confirm_room/", views.confirm_room, name="confirm_room"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("leave_room/", views.leave_room, name="leave_room"),
    path("room/<int:room_id>/", views.room, name="room"),
]