from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse_lazy
from django.utils.encoding import smart_bytes, smart_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, NotFound
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


class ChangePasswordSerializer(serializers.Serializer):
    
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    old_password = serializers.CharField(required=True, min_length=6)
    new_password = serializers.CharField(required=True, min_length=6)

    def validate_old_password(self, old_password):
        if not self.user.check_password(old_password):
            raise serializers.ValidationError("Old password is wrong")
        return old_password

    def save(self):
        self.user.set_password(self.validated_data.get('new_password'))
        self.user.save()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'first_name', 'last_name', 'bio', 'avatar']

    def update(self, instance, validated_data):
        #bulk update the only fields that are supplied using the key
        for key in validated_data.keys():
            setattr(instance, key, validated_data[key])
        instance.save()
        return instance


class EmailPasswordResetSerialiazer(serializers.Serializer):
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
        if user.is_verified:
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            reset_link = self.context['request'].build_absolute_uri(
                reverse_lazy("authentication:verify-password-token", args=(uidb64, token)))
            send_email('authentication/resetpw_mail.html', email_address, reset_link, "QuizBank")


class NewPasswordSerializer(serializers.Serializer):
    
    new_password1 = serializers.CharField(required=True, min_length=6, write_only=True)
    new_password2 = serializers.CharField(required=True, min_length=6, write_only = True)
    token = serializers.CharField(required=True)
    uidb64 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password1'] != attrs['new_password2']:
            raise serializers.ValidationError("Password must match")
        try:
            id = int(smart_str(urlsafe_base64_decode(attrs['uidb64'])))
            user = User.objects.get(id=id)
        except ValueError:
            raise AuthenticationFailed("This token is invalid")
        except User.DoesNotExist:
            raise NotFound("User does not exist")
        if not PasswordResetTokenGenerator().check_token(user, attrs['token']):
            raise AuthenticationFailed("This token is invalid")
        super().validate(attrs)['user'] = user
        return super().validate(attrs)
        
    def save(self):
        self.validated_data.get('user').set_password(self.validated_data.get('new_password1'))
        self.validated_data.get('user').save()
        

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "bio", "is_verified",
        "is_staff","is_superuser", "date_joined", "avatar"]