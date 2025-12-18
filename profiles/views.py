from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import generics, status

from .models import UserProfile
from .serializers import UserProfileSerializer


# Create / Complete Profile
class CompleteProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        # Handle file upload correctly
        profile_data = request.data.copy()
        if 'profile_photo' in request.FILES:
            profile_data['profile_photo'] = request.FILES['profile_photo']

        serializer = UserProfileSerializer(data=profile_data)
        serializer.is_valid(raise_exception=True)

        profile, _ = UserProfile.objects.update_or_create(
            user=request.user,
            defaults={**serializer.validated_data, "is_completed": True},
        )

        return Response(
            {
                "message": "Profile completed successfully.",
                "profile": UserProfileSerializer(profile).data,
            },
            status=status.HTTP_200_OK,
        )


# Retrieve / Update Profile
class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        # Only allow teacher to access their own profile
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)  # Partial update
        instance = self.get_object()

        profile_data = request.data.copy()
        if 'profile_photo' in request.FILES:
            profile_data['profile_photo'] = request.FILES['profile_photo']

        serializer = self.get_serializer(instance, data=profile_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {
                "message": "Profile updated successfully",
                "profile": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# Soft Delete Profile
class UserProfileDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        profile = UserProfile.objects.filter(user=request.user).first()
        if not profile:
            return Response({"message": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Soft delete: mark as incomplete
        profile.is_completed = False
        profile.save(update_fields=["is_completed"])

        return Response({"message": "Profile deleted successfully (soft delete)."}, status=status.HTTP_200_OK)
