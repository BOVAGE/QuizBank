from common.permissions import IsAdminUserOrReadOnly
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import (IsAdminUser, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Category, Question
from .serializers import (CategorySerializer, QuestionDetailSerializer,
                          QuestionPublicSerializer)

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


class StatisticsView(APIView):
    """ 
        returns information about questions, categories
        and activity about the quiz app.

        Optianally return a shorter response by filtering against
        an `on` query parameter in the URL.
    """

    def get(self, request):
        questions = {
            "all_questions": Question.no_of_all_questions(),
            "verified_questions": Question.no_of_verified_questions(),
            "unverified_questions": Question.no_of_unverified_questions()
        }
        difficulty = {
            "easy": Question.no_of_easy_questions(),
            "medium": Question.no_of_medium_questions(),
            "hard": Question.no_of_hard_questions()
        }
        users = {
            "Total Users": User.total_user(),
            "Total Staff": User.total_staff(),
        }
        activity = {
            "last_created": Question.last_created(),
            "last_verified": Question.last_verified(),
        }
        data = {
            "status": "success",
            "message": "Statistics about questions,category, difficulty, users, activity",
            "data": {
                "question": questions,
                "difficulty": difficulty,
                "category": Category.questions_count_category(),
                "users": users,
                "activity": activity, 
            }
        }
        info_on = request.query_params.get('on')
        info_list = ['category', 'difficulty', 'question', 'users', 'activity']
        if info_on is not None and info_on in info_list:
            data = {
            "status": "success",
            "message": f"Statistics on {info_on}",
            "data": {
                info_on: data.get("data")[info_on], 
            }
        }
        return Response(data, status=status.HTTP_200_OK)

class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [IsAdminUserOrReadOnly]
    authentication_classes = [JWTAuthentication]

    def list(self, request, *args, **kwargs):
        data = super().list(request, *args, **kwargs).data
        data = {
            "status": "success",
            "message": "All Categories fetched successfully",
            "data": data
        }
        return Response(data, status=status.HTTP_200_OK)
    def create(self, request, *args, **kwargs):
        data = super().create(request, *args, **kwargs).data
        data = {
            "status": "success",
            "message": f"Category - {data.get('name')} created successfully",
            "data": data
        }
        return Response(data, status=status.HTTP_201_CREATED)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = Category.objects.all()
    lookup_field = "slug"

    def retrieve(self, request, *args, **kwargs):
        data = super().retrieve(request, *args, **kwargs).data
        data = {
            "status": "success",
            "message": f"Category - {data.get('name')} retrieved successfully",
            "data": data
        }
        return Response(data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        data = super().update(request, *args, **kwargs).data
        data = {
            "status": "success",
            "message": f"Category - {data.get('name')} updated successfully",
            "data": data
        }
        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        data = super().destroy(request, *args, **kwargs).data
        data = {
            "status": "success",
            "message": f"Category deleted successfully",
            "data": data
        }
        return Response(data, status=status.HTTP_204_NO_CONTENT)


class UserQuestionListView(generics.ListAPIView):
    serializer_class = QuestionDetailSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id = self.kwargs['id']
        user = get_object_or_404(User, id=id)
        return user.questions.all()

    def list(self, request, *args, **kwargs):
        data = super().list(request, *args, **kwargs).data
        data = {
            "status": "success",
            "message": "Questions created by the user whose ID is passed in the URL fetched successfully",
            "data": data
        }
        return Response(data, status=status.HTTP_200_OK)
    

class UserQuestionStatView(APIView):

    def get(self, request, id):
        user = get_object_or_404(User, id=id)
        data = {
            "status": "success",
            "message": "Statistics on the questions created by the user whose ID is passed in the URL",
            "data": {
                "all_question": user.get_number_of_questions(),
                "verified_questions": user.get_number_of_verified_questions(),
                "unverified_questions": user.get_number_of_unverified_questions(), 
            }
        }
        return Response(data, status=status.HTTP_200_OK)


class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionPublicSerializer
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]
    queryset = Question.objects.all()
    lookup_field = "id"   

    def retrieve(self, request, *args, **kwargs):
        data = super().retrieve(request, *args, **kwargs).data
        data = {
            "status": "success",
            "message": f"Question - {data.get('id')} retrieved successfully",
            "data": data
        }
        return Response(data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        data = super().update(request, *args, **kwargs).data
        data = {
            "status": "success",
            "message": f"Question - {data.get('id')} updated successfully",
            "data": data
        }
        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        data = super().destroy(request, *args, **kwargs).data
        data = {
            "status": "success",
            "message": f"Question deleted successfully",
            "data": data
        }
        return Response(data, status=status.HTTP_204_NO_CONTENT)


QuestionListCreateView = QuestionListCreateView.as_view()
QuestionListFullView = QuestionListFullView.as_view()
UnverifiedQuestionListFullView = UnverifiedQuestionListFullView.as_view()
QuestionVerification = QuestionVerification.as_view()
StatisticsView = StatisticsView.as_view()
CategoryListCreateView = CategoryListCreateView.as_view()
CategoryDetailView = CategoryDetailView.as_view()
UserQuestionListView = UserQuestionListView.as_view()
UserQuestionStatView = UserQuestionStatView.as_view()
QuestionDetailView = QuestionDetailView.as_view()
