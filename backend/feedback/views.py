from common.permissions import IsAdminUserorWriteOnly
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Feedback
from .serializers import FeedbackCreateSerializer, FeedbackSerializer


class FeedbackListView(generics.ListCreateAPIView):
    serializer_class = FeedbackCreateSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserorWriteOnly & IsAuthenticated]
    queryset = Feedback.objects.all()

    def list(self, request, *args, **kwargs):
        data = super().list(request, *args, **kwargs).data
        data = {
            "status": "success",
            "message": "All feedback fetched successfully",
            "data": data,
        }
        return Response(data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        return serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        data = super().create(request, *args, **kwargs).data
        data = {
            "status": "success",
            "message": "Feedback created successfully",
            "data": data,
        }
        return Response(data, status=status.HTTP_201_CREATED)


class FeedbackDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FeedbackSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    queryset = Feedback.objects.all()
    lookup_field = "id"

    def retrieve(self, request, *args, **kwargs):
        data = super().retrieve(request, *args, **kwargs).data
        data = {
            "status": "success",
            "message": f"Feedback retrieved successfully",
            "data": data,
        }
        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        data = super().update(request, *args, **kwargs).data
        data = {
            "status": "success",
            "message": "Feedback updated successfully",
            "data": data,
        }
        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        data = super().destroy(request, *args, **kwargs).data
        data = {
            "status": "success",
            "message": f"Feedback deleted successfully",
            "data": data,
        }
        return Response(data, status=status.HTTP_204_NO_CONTENT)
