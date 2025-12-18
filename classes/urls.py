from django.urls import path
from .views import ClassRoomListCreateView, ClassRoomRetrieveUpdateDestroyView

urlpatterns = [
    path("classes/", ClassRoomListCreateView.as_view(), name="class-list-create"),
    path("classes/<int:pk>/", ClassRoomRetrieveUpdateDestroyView.as_view(), name="class-detail"),
]
