import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from rest_framework import exceptions, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from utils.email import send_email

from .serializers import (ChangePasswordSerializer, LoginSerializer,
                          RegisterSerializer, ResendEmailSerialiazer,
                          UserSerializer)

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
