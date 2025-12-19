from django.db import models
from django.conf import settings
from classes.models import ClassRoom
from subjects.models import Subject

User = settings.AUTH_USER_MODEL

class Exam(models.Model):
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="exams"
    )
    exam_name = models.CharField(max_length=255)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="exams"
    )
    class_name = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name="exams"
    )

    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    total_marks = models.PositiveIntegerField()
    passing_marks = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["exam_date", "start_time"]
        unique_together = ("teacher", "exam_name", "subject", "class_name", "exam_date")

    def __str__(self):
        return f"{self.exam_name} - {self.class_name.name} - {self.subject.name}"
