from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import SmartReviewAPIView

urlpatterns = [
    # Endpoint for generating questions from class notes
    path("generate-questions/", SmartReviewAPIView.as_view(), name="generate-questions"),
]
