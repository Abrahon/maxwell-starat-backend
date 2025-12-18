from rest_framework import serializers
from .models import Subject

class SubjectSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source="class_room.name", read_only=True)

    class Meta:
        model = Subject
        fields = [
            "id",
            "name",
            "code",
            "class_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "class_name", "created_at", "updated_at", "class_room"]

    def create(self, validated_data):
        user = self.context['request'].user
        class_room = user.classes.first()  # auto-assign teacher's first class
        validated_data['class_room'] = class_room
        return super().create(validated_data)

    def validate_name(self, value):
        user = self.context['request'].user
        class_room = user.classes.first()
        subject_id = self.instance.id if self.instance else None
        if Subject.objects.filter(class_room=class_room, name=value).exclude(id=subject_id).exists():
            raise serializers.ValidationError("Subject with this name already exists in your class.")
        return value

    def validate_code(self, value):
        user = self.context['request'].user
        class_room = user.classes.first()
        subject_id = self.instance.id if self.instance else None
        if Subject.objects.filter(class_room=class_room, code=value).exclude(id=subject_id).exists():
            raise serializers.ValidationError("Subject with this code already exists in your class.")
        return value
