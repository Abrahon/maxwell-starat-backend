from django.urls import path
from .views import CompleteProfileView, UserProfileDetailView, UserProfileDeleteView

urlpatterns = [
    path("profile/complete/", CompleteProfileView.as_view(), name="profile-complete"),
    path("profile/", UserProfileDetailView.as_view(), name="profile-detail"),
    path("profile/delete/", UserProfileDeleteView.as_view(), name="profile-delete"),
]
