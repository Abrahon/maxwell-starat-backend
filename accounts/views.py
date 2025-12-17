from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.urls import reverse
import logging

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
import logging
from .models import User, EmailVerification
from .serializers import SignupSerializer
from .utils import send_email_verification
from .enums import RoleChoices

logger = logging.getLogger(__name__)
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken

from .models import OTP, EmailVerification
from .serializers import (
    SignupSerializer,
    LoginSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer,
    UserSerializer,
    EmailVerificationSerializer
)
from .utils import generate_otp, send_otp_email

User = get_user_model()


# ---------------------------
# JWT TOKEN GENERATOR
# ---------------------------
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token)
    }


class SignupView(generics.GenericAPIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        # Check if a user already exists
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return Response(
                    {"email": "This email is already registered."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                # User exists but inactive → resend verification email
                verification = EmailVerification.objects.filter(user=user).first()
                if not verification:
                    verification = EmailVerification.objects.create(user=user)
                    print("verification",verification)

                verification_link = f"{request.scheme}://{request.get_host()}/auth/verify-email/{verification.token}/"

                print("verification_link",verification_link)
                try:
                    send_email_verification(email, verification_link)
                except Exception as e:
                    logger.exception("Failed to send verification email to %s: %s", email, e)

                return Response(
                    {"message": "Verification email resent. Please check your inbox."},
                    status=status.HTTP_200_OK
                )

        except User.DoesNotExist:
            # No user exists → create new inactive user
            user = User.objects.create_user(
                email=email,
                password=password,
                is_active=False,
                role=RoleChoices.TEACHER  # default role
            )

            verification = EmailVerification.objects.create(user=user)
            verification_link = f"{request.scheme}://{request.get_host()}/verify-email/{verification.token}/"
            print("verification_link",verification_link)
            try:
                send_email_verification(email, verification_link)
            except Exception as e:
                logger.exception("Failed to send verification email to %s: %s", email, e)

            return Response(
                {"message": "User created. Check your email to verify your account."},
                status=status.HTTP_201_CREATED
            )

# ---------------------------
# VERIFY SIGNUP OTP AND CREATE USER
# ---------------------------

# email verifications
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        serializer = EmailVerificationSerializer(data={"token": token})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"message": "Email verified successfully."}, status=200)



# ---------------------------
# LOGIN VIEW
# ---------------------------
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        if not user.is_active:
            return Response({"detail": "Email not verified."}, status=400)

        tokens = get_tokens_for_user(user)
        user_data = UserSerializer(user).data

        return Response({
            "message": "Login successful",
            "tokens": tokens,
            "user": user_data
        }, status=200)


# ---------------------------
# SEND OTP (FOR RESET PASSWORD)
# ---------------------------
class SendOTPView(generics.CreateAPIView):
    serializer_class = SendOTPSerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = serializer.save()  
        print("serializer.save() returned:", result)

        # ❌ ISSUE IS HERE:
        # serializer.save() is returning a User object, NOT a dict.
        # User object has NO .get() method — that's why error occurred:
        # AttributeError: 'User' object has no attribute 'get'

        email = serializer.validated_data.get("email")
        if email and hasattr(request, "session"):
            request.session['otp_user_email'] = email
            print("Stored in session:", email)

        return Response(
            {"message": "OTP sent successfully", "email": email},
            
            status=200
        )


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        # OTP verified → keep email in session for password reset
        request.session['verified_email'] = serializer.validated_data["user"].email

        return Response({"message": "OTP verified successfully."})

# ---------------------------
# RESET PASSWORD USING OTP
# ---------------------------
class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        otp_code = request.data.get("otp")

        if not email or not otp_code:
            return Response({"detail": "Email and OTP required."}, status=400)

        user = get_object_or_404(User, email=email)
        otp_instance = OTP.objects.filter(user=user, code=otp_code).order_by("-created_at").first()
        if not otp_instance or otp_instance.is_expired():
            return Response({"detail": "Invalid or expired OTP."}, status=400)

        # Delete OTP
        otp_instance.delete()

        # Reset password
        serializer = self.get_serializer(data=request.data, context={"user": user})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Password reset successfully."}, status=200)


# ---------------------------
# LIST USERS (ADMIN ONLY)
# ---------------------------
class UserListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = None  # Add pagination if needed

    def get_queryset(self):
        role = self.request.query_params.get("role")
        qs = super().get_queryset()
        if role:
            qs = qs.filter(role=role)
        return qs


# ---------------------------
# DELETE USER (ADMIN ONLY)
# ---------------------------
class AdminDeleteUserView(generics.DestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    lookup_field = "id"

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        if user.is_superuser:
            return Response({"detail": "Cannot delete superuser."}, status=403)
        user.delete()
        return Response({"detail": f"User {user.email} deleted successfully."}, status=200)


# ---------------------------
# CHANGE PASSWORD (LOGGED IN USER)
# ---------------------------
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ResetPasswordSerializer  # Can create separate ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"user": self.get_object()})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password changed successfully."}, status=200)
