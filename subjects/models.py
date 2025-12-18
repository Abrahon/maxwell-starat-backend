from django.db import models
from classes.models import ClassRoom

class Subject(models.Model):
    class_room = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name="subjects"
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["class_room", "name"],
                name="unique_subject_name_per_class"
            ),
            models.UniqueConstraint(
                fields=["class_room", "code"],
                name="unique_subject_code_per_class"
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.class_room.name})"
