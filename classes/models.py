from django.conf import settings
from django.db import models


class ClassRoom(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="classes"
    )

    name = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Class name (e.g., Class 10, Grade 8)"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "name"],
                name="unique_class_per_teacher"
            )
        ]
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    def __str__(self):
        return f"{self.name}"
