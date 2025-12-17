from django.db.models import TextChoices

class RoleChoices(TextChoices):
    ADMIN = 'admin', 'Admin'
    TEACHER = 'teacher', 'Teacher'