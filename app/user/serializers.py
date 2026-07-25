# accounts/serializers.py

from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


# JWT response serializer
class TokenResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    token_type = serializers.CharField(default="bearer")
    is_verified = serializers.BooleanField()


# User registration
class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    class Meta:
        model = User

        fields = (
            "id",
            "username",
            "email",
            "is_verified",
            "password",
            "role",
        )

        read_only_fields = ("id", "is_verified")

    # Prevent admin registration
    def validate_role(self, value):

        if value == User.Role.ADMIN:
            raise serializers.ValidationError(
                "Admin users cannot be created publicly."
            )

        return value

    # Create user
    def create(self, validated_data):

        password = validated_data.pop("password")

        user = User(**validated_data)

        user.set_password(password)

        user.save()

        return user


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class TokenValidationSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()


class ResetPasswordSerializer(TokenValidationSerializer):
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                "New password and confirm password do not match."
            )
        return attrs


class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Password is incorrect.")
        return value


# Login serializer
class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):

        request = self.context.get("request")

        user = authenticate(
            request=request,
            username=attrs["email"],
            password=attrs["password"],
        )

        if not user:
            raise serializers.ValidationError(
                "Invalid credentials."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This account is disabled."
            )

        attrs["user"] = user

        return attrs


# User profile serializer
class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = (
            "id",
            "email",
            "username",
            "role",
            "is_verified",
        )

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=(
            'username',
            'email',
            'role',
            'is_verified',
        )
        read_only_fields=(
            'role',
            'is_verified',
        )
    def validate_email(self,value):
        user=self.context['request'].user
        if (User.objects.filter(email=value).exclude(id=user.id).exists()):
            raise serializers.ValidationError(
                "This email is already in use."
            )
        return value

    def update(self, instance, validated_data):
        if "email" in validated_data and validated_data["email"] != instance.email:
            instance.is_verified = False
        return super().update(instance, validated_data)

class ChangePasswordSerializer(serializers.Serializer):
    old_password=serializers.CharField(write_only=True)
    new_password=serializers.CharField(write_only=True,min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    def validate_old_password(self,value):
        user=self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                "Old password is incorrect."
            )
        return value
    def validate(self,attrs):
        if attrs['new_password']!=attrs['confirm_password']:
            raise serializers.ValidationError(
                "New password and confirm password do not match."
            )
        validate_password(
            attrs["new_password"],
            self.context["request"].user,
        )
        return attrs
    def save(self,**kwargs):
        user=self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=["password"])
        return user
