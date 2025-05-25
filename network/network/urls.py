
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("posts", views.all_posts, name="all_posts"),
    path("create", views.create_post, name="create_post"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("follow/<str:username>", views.follow_toggle, name="follow"),
    path("following", views.following_posts, name="following"),
    path("edit/<int:post_id>", views.edit_post, name="edit"),
    path("like/<int:post_id>", views.like_post, name="like"),
]
