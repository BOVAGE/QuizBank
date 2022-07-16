from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Question
from .serializers import QuestionDetailSerializer, QuestionPublicSerializer

User = get_user_model()
class QuestionListCreateView(generics.GenericAPIView):
    """ 
        Public questions endpoint
    """
    serializer_class = QuestionPublicSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Question.verified.random_all()
        limit = self.request.query_params.get('limit')
        category = self.request.query_params.get('category')
        difficulty = self.request.query_params.get('difficulty')
        type = self.request.query_params.get('type')
        search = self.request.query_params.get('search')
        if category is not None:
            print("category", category)
            queryset = queryset.filter(category__slug=category)
        if difficulty is not None:
            print("difficulty", difficulty)
            queryset = queryset.filter(difficulty=difficulty)
        if type is not None:
            print("type", type)
            queryset = queryset.filter(type=type)
        if limit is not None:
            print("limit", limit)
            try:
                limit = int(limit)
                queryset = queryset[:limit]
            except ValueError:
                pass
        if search is not None:
            search_query = Q(question__icontains=search) | Q(explanation__icontains=search)
            search_queryset = Question.verified.filter(search_query)
            return search_queryset
        return queryset[:50]

    def get(self, request):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        data = {
            "status": "success",
            "message": "Question fetched successfully",
            "data": serializer.data
        }
        return Response(data, status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        data = {
            "status": "success",
            "message": "Question created successfully",
            "data": serializer.data
        }
        return Response(data, status.HTTP_201_CREATED)


class QuestionListFullView(generics.ListAPIView):
    serializer_class = QuestionDetailSerializer
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]
    queryset = Question.objects.order_by("-date_created")

    def list(self, request, *args, **kwargs):
        data = super().list(request, *args, **kwargs).data
        data = {
            "status": "success",
            "message": "All Questions fetched successfully",
            "data": data
        }
        return Response(data, status=status.HTTP_200_OK)


class UnverifiedQuestionListFullView(generics.ListAPIView):
    serializer_class = QuestionDetailSerializer
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]
    queryset = Question.unverified.order_by("-date_created")

    def list(self, request, *args, **kwargs):
        data = super().list(request, *args, **kwargs).data
        data = {
            "status": "success",
            "message": "All Unverified Questions fetched successfully",
            "data": data
        }
        return Response(data, status=status.HTTP_200_OK)


class QuestionVerification(APIView):
    """
        verify or unverify the question whose ID was passed in the URL
    """
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]

    def post(self, request, id):
        """
            verifies the question whose ID was passed in the URL
        """
        question = get_object_or_404(Question, id=id)
        question.verify(request.user)
        data = {
            "status": "success",
            "message": f"{request.user} verifies question-{question.id}: {question}",
            "data": []
        }
        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        """
            unverifies the question whose ID was passed in the URL
        """
        question = get_object_or_404(Question, id=id)
        question.unverify()
        data = {
            "status": "success",
            "message": f"{request.user} unverifies question-{question.id}: {question}",
            "data": []
        }
        return Response(data, status=status.HTTP_200_OK)


QuestionListCreateView = QuestionListCreateView.as_view()
QuestionListFullView = QuestionListFullView.as_view()
UnverifiedQuestionListFullView = UnverifiedQuestionListFullView.as_view()
QuestionVerification = QuestionVerification.as_view()
