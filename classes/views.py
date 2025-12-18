from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import ClassRoom
from .serializers import ClassRoomSerializer

# List & Create Classes (Teacher-owned)
class ClassRoomListCreateView(generics.ListCreateAPIView):
    serializer_class = ClassRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only classes owned by the logged-in teacher
        return ClassRoom.objects.filter(teacher=self.request.user)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"message": "Class created successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )


# Retrieve, Update, Delete Single Class
class ClassRoomRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClassRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only allow teacher to access their own classes
        return ClassRoom.objects.filter(teacher=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"message": "Class updated successfully", "data": serializer.data})

    def destroy(self, request, *args, **kwargs):
        # Hard delete (optional: can be changed to soft delete)
        classroom = self.get_object()
        classroom.delete()
        return Response({"message": "Class deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
