from django.urls import path
from django.contrib.auth.views import LoginView
from .views import (
    set_cookie_view,
    get_cookie_view,
    set_session_view,
    get_session_view,
    # logout_view,
    MyLogoutView,
    AboutMeView,
    RegisterView,
    FooBarView,
    ProfileView,
    UserListView,
    HelloView,

)

app_name = "myauth"

urlpatterns = [
    path(
        "login/",
        LoginView.as_view(
            template_name="myauth/login.html",
            redirect_authenticated_user=True,
        ),
        name="login"),
    path("hello/", HelloView.as_view(), name="hello"),
    # path("logout/", logout_view, name="logout"),
    path("logout/", MyLogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("users/", UserListView.as_view(), name="users_list"),
    path("profile/<int:pk>", ProfileView.as_view(), name="profile"),


    path("cookie/get", get_cookie_view, name="cookie-get"),
    path("cookie/set", set_cookie_view, name="cookie-set"),
    path("session/set", set_session_view, name="session-set"),
    path("session/get", get_session_view, name="session-get"),

    path("about-me/", AboutMeView.as_view(), name="about-me"),

    path("foo-bar/", FooBarView.as_view(), name="foo-bar"),
]