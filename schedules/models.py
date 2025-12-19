from django.db import models
from django.conf import settings
from classes.models import ClassRoom
from subjects.models import Subject

User = settings.AUTH_USER_MODEL

DURATION_CHOICES = [
    ("1 Month", "1 Month"),
    ("2 Months", "2 Months"),
    ("3 Months", "3 Months"),
]

DAYS_OF_WEEK = [
    ("Sat", "Saturday"),
    ("Sun", "Sunday"),
    ("Mon", "Monday"),
    ("Tue", "Tuesday"),
    ("Wed", "Wednesday"),
    ("Thu", "Thursday"),
    ("Fri", "Friday"),
]

class Schedule(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="schedules")
    class_name = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="schedules")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="schedules")

    day_of_week = models.CharField(max_length=3, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration = models.CharField(max_length=10, choices=DURATION_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["day_of_week", "start_time"]
        unique_together = ("teacher", "class_name", "subject", "day_of_week", "start_time")

    def __str__(self):
        return f"{self.teacher} - {self.class_name} - {self.subject} on {self.day_of_week}"
