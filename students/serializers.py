from rest_framework import serializers
from .models import Student

class StudentSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source="class_room.name", read_only=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "full_name",
            "roll_number",
            "email",
            "class_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "class_name", "class_room"]

    def create(self, validated_data):
        user = self.context['request'].user
        class_room = user.classes.first()  # assign teacher's first class
        validated_data['class_room'] = class_room
        return super().create(validated_data)

    def validate_roll_number(self, value):
        user = self.context['request'].user
        class_room = user.classes.first()
        student_id = self.instance.id if self.instance else None
        if Student.objects.filter(class_room=class_room, roll_number=value).exclude(id=student_id).exists():
            raise serializers.ValidationError("Student with this roll number already exists in your class.")
        return value

    def validate_email(self, value):
        user = self.context['request'].user
        class_room = user.classes.first()
        student_id = self.instance.id if self.instance else None
        if Student.objects.filter(class_room=class_room, email=value).exclude(id=student_id).exists():
            raise serializers.ValidationError("Student with this email already exists in your class.")
        return value
