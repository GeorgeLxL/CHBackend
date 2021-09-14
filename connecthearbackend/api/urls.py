from django.conf.urls import url
from django.urls import path
from connecthearbackend.api.views import  UserLoginView, UserRegistrationView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    path('signup', UserRegistrationView.as_view()),
    path('login', UserLoginView.as_view())
]