from django.urls import path

from .views import (ChangePasswordView, EmailVerificationView, LoginView,
                    RegisterView, ResendEmailVerificationView,
                    ResetPasswordView, SetNewPasswordView, UserView,
                    VerifyPasswordTokenView)

app_name = "authentication"
urlpatterns = [
    path('login', LoginView.as_view(), name="login"),
    path('register', RegisterView.as_view(), name="register"),
    path('email-verify', EmailVerificationView.as_view(), name="email-verify"),
    path('resend-email-token', ResendEmailVerificationView.as_view(), name="resend-email-verify"),
    path('change-password', ChangePasswordView.as_view(), name="change-password"),
    path('user-profile', UserView.as_view(), name="user-profile"),
    path('reset-password', ResetPasswordView.as_view(), name="reset-password"),
    path('reset-password/<str:uidb64>/<token>', VerifyPasswordTokenView.as_view(), name="verify-password-token"),
    path('reset-password/set', SetNewPasswordView.as_view(), name="reset-password-set"),
]
