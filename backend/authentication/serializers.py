from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from django.urls import reverse_lazy
from utils.email import send_email

User = get_user_model()

class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, write_only = True)
    username = serializers.CharField(min_length=3)
    class Meta:
        model = User
        fields = ['username', 'password']

    def validate(self, attrs):
        username = attrs['username']
        password = attrs['password']
        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid Credentials or details")
        if not user.is_verified:
            raise serializers.ValidationError("Email verification required.")
        return super().validate(attrs)

    def save(self):
        """ output token pair for user"""
        username = self.validated_data['username']
        password = self.validated_data['password']
        user = authenticate(username=username, password=password)
        return user.get_tokens_for_user()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, write_only = True)
    password2 = serializers.CharField(min_length=6, write_only = True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Password must match")
        return super().validate(attrs)


class ResendEmailSerialiazer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist")
        return email

    def save(self):
        email_address = self.validated_data.get('email')
        user = User.objects.get(email=email_address)
        if not user.is_verified:
            activation_link = self.context['request'].build_absolute_uri(reverse_lazy("authentication:email-verify"))
            activation_link += f'?token={user.get_tokens_for_user()["access"]}'
            print("sending mail")
            send_email('authentication/activate_mail.html', email_address, activation_link, 'QuizBank')