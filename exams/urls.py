from django.urls import path
from .views import ExamListCreateView, ExamRetrieveUpdateDestroyView

urlpatterns = [
    # List all exams / Create new exam
    path('exams/', ExamListCreateView.as_view(), name='exam-list-create'),

    # Retrieve / Update / Delete a specific exam by ID
    path('exams/<int:pk>/', ExamRetrieveUpdateDestroyView.as_view(), name='exam-detail'),
]
