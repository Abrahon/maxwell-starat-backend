from rest_framework import serializers
from .models import Schedule


class ScheduleSerializer(serializers.ModelSerializer):
    # Read-only display fields
    class_display = serializers.CharField(
        source="class_name.name", read_only=True
    )
    subject_display = serializers.CharField(
        source="subject.name", read_only=True
    )

    # WRITE-ONLY field for multiple days
    days = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[choice[0] for choice in Schedule._meta.get_field("day_of_week").choices]
        ),
        write_only=True
    )

    class Meta:
        model = Schedule
        fields = [
            "id",
            "class_name",
            "subject",

            "class_display",
            "subject_display",

            # use "days" instead of day_of_week
            "days",

            "start_time",
            "end_time",
            "duration",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "class_display",
            "subject_display",
        ]

    def validate(self, attrs):
        start_time = attrs["start_time"]
        end_time = attrs["end_time"]

        if start_time >= end_time:
            raise serializers.ValidationError(
                "Start time must be before end time."
            )

        teacher = self.context["request"].user
        class_obj = attrs["class_name"]
        subject = attrs["subject"]

        for day in attrs["days"]:
            if Schedule.objects.filter(
                teacher=teacher,
                class_name=class_obj,
                subject=subject,
                day_of_week=day,
                start_time__lt=end_time,
                end_time__gt=start_time,
            ).exists():
                raise serializers.ValidationError(
                    f"Schedule overlaps on {day}."
                )

        return attrs

    def create(self, validated_data):
        days = validated_data.pop("days")
        teacher = self.context["request"].user

        schedules = []
        for day in days:
            schedules.append(
                Schedule.objects.create(
                    teacher=teacher,
                    day_of_week=day,
                    **validated_data
                )
            )

        return schedules[0]  # DRF requires a single instance
