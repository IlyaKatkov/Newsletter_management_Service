from django.contrib.auth.views import LogoutView
from django.urls import path

from user.apps import UserConfig
from user.views import *

app_name = UserConfig.name

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('email-confirmation-sent/', EmailConfirmationSentView.as_view(), name='email_confirmation_sent'),
    path('activate-user/<str:token>/', VerifyEmailView.as_view(), name='activate_user'),
    path('email-confirmed/', EmailConfirmedView.as_view(), name='email_confirmed'),
    path('confirm-email-failed/', EmailConfirmationFailedView.as_view(), name='email_confirmation_failed'),
    path('password-reset/', UserForgotPasswordView.as_view(), name='password_reset'),
    path('password-reset-sent/', PasswordResetSentView.as_view(), name='password-reset-sent'),
    path('reset/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('users_list/', get_users_list, name='list_users'),
    path('update_user/<int:pk>/', UserUpdateView.as_view(), name='user_update'),
]