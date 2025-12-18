from rest_framework import serializers
from .models import ClassRoom

class ClassRoomSerializer(serializers.ModelSerializer):
    teacher = serializers.ReadOnlyField(source="teacher.id")  # teacher comes from auth user

    class Meta:
        model = ClassRoom
        fields = ["id", "name", "teacher", "created_at"]
        read_only_fields = ["id", "teacher", "created_at"]

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Class name must be at least 3 characters long.")
        return value
