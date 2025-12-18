from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    profile_photo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "full_name",
            "institution_name",
            "country",
            "designation",
            "subject",
            "profile_photo",  # same field for upload & display
            "is_completed",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_completed", "created_at", "updated_at"]

    def to_representation(self, instance):
        """Return full Cloudinary URL for profile_photo when reading."""
        ret = super().to_representation(instance)
        if instance.profile_photo:
            ret["profile_photo"] = instance.profile_photo.url
        return ret

    def validate_full_name(self, value):
        if len(value.split()) < 2:
            raise serializers.ValidationError("Please enter your full name.")
        return value

    def validate_institution_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Institution name cannot be empty.")
        return value
