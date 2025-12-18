from django.db import models
from classes.models import ClassRoom

class Student(models.Model):
    class_room = models.ForeignKey(
        ClassRoom,
        on_delete=models.SET_NULL,
        related_name="students",
        null=True,
        blank=True
    )

    full_name = models.CharField(max_length=150)
    roll_number = models.CharField(max_length=50)  # remove unique=True
    email = models.EmailField()  # remove unique=True
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["class_room", "roll_number"],
                name="unique_roll_per_class"
            ),
            models.UniqueConstraint(
                fields=["class_room", "email"],
                name="unique_email_per_class"
            ),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.roll_number})"
