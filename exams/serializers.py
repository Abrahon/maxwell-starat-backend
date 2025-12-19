from rest_framework import serializers
from .models import Exam

class ExamSerializer(serializers.ModelSerializer):
    class_display = serializers.CharField(source="class_name.name", read_only=True)
    subject_display = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = Exam
        fields = [
            "id",
            "teacher",
            "exam_name",
            "subject",
            "subject_display",
            "class_name",
            "class_display",
            "exam_date",
            "start_time",
            "end_time",
            "total_marks",
            "passing_marks",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "teacher", "subject_display", "class_display", "created_at", "updated_at"]

    def validate(self, attrs):
        start_time = attrs.get("start_time")
        end_time = attrs.get("end_time")
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("Start time must be before end time.")

        total_marks = attrs.get("total_marks")
        passing_marks = attrs.get("passing_marks")
        if total_marks is not None and passing_marks is not None:
            if passing_marks > total_marks:
                raise serializers.ValidationError("Passing marks cannot exceed total marks.")
        
        return attrs

    def create(self, validated_data):
        validated_data["teacher"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data["teacher"] = self.context["request"].user
        return super().update(instance, validated_data)