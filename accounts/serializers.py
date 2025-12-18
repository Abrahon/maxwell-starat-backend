
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.core.validators import RegexValidator
from .models import OTP
from .utils import generate_otp, send_otp_email

User = get_user_model() 
# ---------------------------
# SIGNUP SERIALIZER
# ---------------------------
from rest_framework import serializers
from django.core.validators import RegexValidator
from .models import User # make sure RoleChoices exists
from .models import EmailVerification, User

from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import OTP

User = get_user_model()


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={
            "invalid": "Enter a valid email address.",
            "required": "Email field is required.",
            "blank": "Email cannot be empty."
        }
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        error_messages={
            "min_length": "Password must be at least 8 characters long.",
            "blank": "Password field cannot be empty.",
        },
    )

    confirm_password = serializers.CharField(
        write_only=True,
        min_length=8,
        error_messages={
            "min_length": "Confirm password must be at least 8 characters long.",
            "blank": "Confirm password field cannot be empty.",
        },
    )

    def validate_email(self, value):
        # Only block if an ACTIVE user exists with the same email
        if User.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return attrs



class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.UUIDField()

    class Meta:
        model = EmailVerification
        fields = ['token']

    def save(self, **kwargs):
        token = self.validated_data['token']
        try:
            verification = EmailVerification.objects.get(token=token)
            user = verification.user
            user.is_active = True
            user.save()
            verification.delete()  # optional: remove verification record
            return user
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired token")


# ---------------------------
# LOGIN SERIALIZER
# ---------------------------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")
        attrs["user"] = user
        return attrs


class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def create(self, validated_data):
        user = User.objects.get(email=validated_data["email"])

        # Generate OTP
        code = generate_otp()
        OTP.objects.create(user=user, code=code)

        # Send OTP using default name
        send_otp_email(user.email, code, name="User")  # always "User" since no name fields

        return user



class VerifyOTPSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        request = self.context.get("request")
        email = request.data.get("email")

        if not email:
            raise serializers.ValidationError(
                "No OTP request found. Please request OTP first."
            )

        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("User not found.")

        otp = OTP.objects.filter(user=user, code=data["code"]).order_by("-created_at").first()
        if not otp or otp.is_expired():
            raise serializers.ValidationError("OTP is invalid or expired.")

        data["user"] = user
        return data

# ---------------------------
# RESET PASSWORD SERIALIZER
# ---------------------------
class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")

        user = self.context.get("user")
        if not user:
            raise serializers.ValidationError("OTP verification required.")
        self.user = user
        return attrs

    def save(self, **kwargs):
        self.user.set_password(self.validated_data["new_password"])
        self.user.save()
        OTP.objects.filter(user=self.user).delete()
        return self.user


# ---------------------------
# CHANGE PASSWORD SERIALIZER
# ---------------------------
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError("Old password is incorrect.")
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email', 'role', 'is_active']