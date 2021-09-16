from django.conf.urls import url
from django.urls import path
from connecthearbackend.api.views import  UserLoginView, UserRegistrationView, CurrencyView, AdminLoginView, UploadView, Account, UserList, AccountUpdate,AvatarUpdate
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    path('signup', UserRegistrationView.as_view()),
    path('login', UserLoginView.as_view()),
    path('myadmin/login', AdminLoginView.as_view()),
    path('getProfile', Account.as_view(), name="account_register"),
    path('updateProfile', AccountUpdate.as_view(), name="account_register"),
    path('updateAvatar', AvatarUpdate.as_view(), name="account_register"),
    path('getusers', UserList.as_view()),
    path('uploadcsv', UploadView.as_view())
    
]