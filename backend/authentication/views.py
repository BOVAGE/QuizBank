import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.encoding import smart_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import exceptions, generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenRefreshView
from utils.email import send_email

from .serializers import (AdminUserSerializer, ChangePasswordSerializer,
                          EmailPasswordResetSerialiazer, LoginSerializer,
                          NewPasswordSerializer, RegisterSerializer,
                          ResendEmailSerialiazer, UserSerializer)

User = get_user_model()

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.save()
        data = {
            "status": "success",
            "message": "Login credentials are  valid",
            "data": {**serializer.data, **tokens}
        }
        return Response(data, status=status.HTTP_200_OK)


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        email_address = serializer.data['email']
        data = {
            "status": "success",
            "message": "An email activation link has been to your email address",
            "data": serializer.data
        }
        # send account activation email
        activation_link = request.build_absolute_uri(reverse_lazy("authentication:email-verify"))
        activation_link += f'?token={user.get_tokens_for_user()["access"]}'
        send_email('authentication/activate_mail.html', email_address, activation_link, 'QuizBank')
        return Response(data, status=status.HTTP_201_CREATED)

class EmailVerificationView(APIView):
    
    def get(self, request):
        token = request.GET.get('token')
        ALGORITHM = settings.SIMPLE_JWT['ALGORITHM']
        SIGNING_KEY = settings.SIMPLE_JWT['SIGNING_KEY']
        try:
            payload = jwt.decode(token, SIGNING_KEY, algorithms=[ALGORITHM])
            user = User.objects.get(id=payload.get('user_id'))
        except (jwt.DecodeError, User.DoesNotExist) as e:
            raise exceptions.AuthenticationFailed("Your token is invalid")
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Your Token has expired!")
        else:
            if not user.is_verified:
                user.is_verified = True
                user.save()
                data = {
                    "status": "success",
                    "message": "Account has been verified successfully",
                    "data": []
                }
                return Response(data, status=status.HTTP_200_OK)
            data = {
                "status": "failed",
                "message": "Account has has been verified previously",
                "data": []
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class ResendEmailVerificationView(generics.GenericAPIView):
    serializer_class = ResendEmailSerialiazer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {
            'status': 'success',
            'message': 'Email account verification mail sent',
            'data': serializer.data,
        }
        return Response(data, status.HTTP_200_OK)

class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = self.serializer_class(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {
            'status': 'success',
            'message': 'Password Updated Successfully',
            'data': []
        }
        return Response(data, status.HTTP_200_OK)


class UserView(generics.GenericAPIView):
    """
        get user authenticated user profile and update it.
    """
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = self.serializer_class(request.user)
        data = {
            'status': 'success',
            'message': 'Authenticated User Profile',
            'data': serializer.data,
        }
        return Response(data, status.HTTP_200_OK)


    def patch(self, request):
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {
            'status': 'success',
            'message': 'Profile Updated Successfully',
            'data': serializer.data,
        }
        return Response(data, status.HTTP_200_OK)


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = EmailPasswordResetSerialiazer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {
            'status': 'success',
            'message': 'Password reset mail sent',
            'data': serializer.data
        }
        return Response(data, status.HTTP_200_OK)


class VerifyPasswordTokenView(APIView):
    
    def get(self,request, uidb64, token):
        try:
            id = int(smart_str(urlsafe_base64_decode(uidb64)))
            user = User.objects.get(id=id)
        except ValueError:
            data = {
                "status": "failed",
                "message": "This token is invalid",
                "data": []
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            data = {
                "status": "failed",
                "message": "User does not exist",
                "data": []
            }
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        if not PasswordResetTokenGenerator().check_token(user, token):
            data = {
                "status": "failed",
                "message": "This token is invalid",
                "data": []
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)
        data = {
            'status': 'success',
            'message': 'Token is valid',
            'data': {
                'token': token,
                'uidb64': uidb64
            }
        }
        return Response(data, status.HTTP_200_OK)

class SetNewPasswordView(generics.GenericAPIView):
    serializer_class = NewPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {
            "status": "success",
            "message": "Password Reset Done successfully",
            "data": []
        }
        return Response(data, status.HTTP_200_OK)


class UserStaff(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request, id):
        """
            make a user whose ID is passed in URL a staff
        """
        user = get_object_or_404(User, id=id)
        if user.is_staff:
            data = {
                "status": "failed",
                "message": f"{user.username} is a staff user",
                "data": []
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        user.is_staff = True
        user.save()
        # send `you are now a staff` email
        send_email('authentication/now_staff_mail.html', user.email, link="", site_name='QuizBank')
        data = {
            "status": "success",
            "message": f"{user.username} has been made a staff and an email has been sent to {user.email}",
            "data": []
        }
        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        """
            make a user whose ID is passed in URL a non-staff
        """
        user = get_object_or_404(User, id=id)
        if user.is_staff:
            user.is_staff = False
            user.save()
            # send `you are no longer a staff` email
            send_email('authentication/no_longer_staff_mail.html', user.email, link="", site_name='QuizBank')
            data = {
                "status": "success",
                "message": f"{user.username} is no longer a staff and an email has been sent to {user.email}",
                "data": []
            }
            return Response(data, status=status.HTTP_200_OK)
        data = {
            "status": "success",
            "message": f"{user.username} is not a staff",
            "data": []
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]
    queryset = User.objects.all()

    def list(self, request, *args, **kwargs):
        data = super().list(request, *args, **kwargs).data
        data = {
            "status": "success",
            "message": "Details about all users",
            'data': data
        }
        return Response(data, status=status.HTTP_200_OK)


class CustomTokenRefreshView(TokenRefreshView):
    
    def post(self, request, *args, **kwargs):
        data = super().post(request, *args, **kwargs).data
        data = {
            "status": "success",
            "message": "New access token",
            "data": data
        }

        return Response(data, status=status.HTTP_200_OK)