from random import random

from django.contrib.auth.decorators import (
    login_required,
    permission_required,
    user_passes_test,
   )

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    TemplateView,
    CreateView,
    UpdateView,
    ListView
)

from .forms import ProfileForm
from .models import Profile
from django.utils.translation import gettext_lazy as _, ngettext
from django.views.decorators.cache import cache_page



class HelloView(View):
    welcome_message = _("welcome Hello World!")

    def get(self, request: HttpRequest) -> HttpResponse:
        items_str = request.GET.get("items") or 0
        items = int(items_str)
        products_line = ngettext(
            "product",
            "{count} products",
            items,
        )

        products_line = products_line.format(count=items)
        return HttpResponse(
            f"<h1>{self.welcome_message}</h1>"
            f"\n<h2>{products_line}</h2>"
        )


class UserListView(ListView):
    model = User
    template_name = 'myauth/users-list.html'
    context_object_name = "users"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_user'] = self.request.user
        return context


class AboutMeView(TemplateView):
    template_name = "myauth/about-me.html"


class ProfileView(UserPassesTestMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name_suffix = "_update_form"
    success_url = reverse_lazy("myauth:about-me")
    context_object_name = "profile"

    def test_func(self):
        no_superuser_get_access = False

        profile_author = self.get_object().user
        if profile_author == self.request.user:
            no_superuser_get_access = True

        return any([self.request.user.is_superuser, no_superuser_get_access])


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"

    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(
            self.request,
            username=username,
            password=password,
        )
        login(request=self.request, user=user)
        return response

    def get_success_url(self):
        profile = Profile.objects.create(user=self.object)
        return reverse(
            "myauth:profile",
             kwargs={"pk": profile.pk},
        )


# def login_view(request: HttpRequest) -> HttpResponse:
#     if request.method == "GET":
#         if request.user.is_authenticated:
#             return redirect("/admin/")
#
#         return render(request, 'myauth/login.html')
#
#     username = request.POST["username"]
#     password = request.POST["password"]
#
#     user = authenticate(request, username=username, password=password)
#     if user is not None:
#         login(request, user)
#         return redirect('/admin/')
#
#     return render(request, "myauth/login.html", {"error": "Invalid login credentials"})


def logout_view(request: HttpRequest):
    logout(request)
    return redirect(reverse("myauth:login"))


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie_set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response


@cache_page(60)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default_value")
    return HttpResponse(f"Cookie value {value!r} + {random()}")


@permission_required("myauth:view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session Set!")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default value")
    return HttpResponse(f"Session value: {value!r}")


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})
