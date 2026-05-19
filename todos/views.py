from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Comment, Label, Task, Todo
from .presenters import category_to_dict, comment_to_dict, label_to_dict, task_to_dict, todo_to_dict, user_to_dict
from .schemas import (
    CategoryCreateSchema,
    CategoryUpdateSchema,
    CommentCreateSchema,
    CommentUpdateSchema,
    LabelCreateSchema,
    LabelUpdateSchema,
    RegisterCreateSchema,
    TaskCreateSchema,
    TaskUpdateSchema,
    TodoCreateSchema,
    TodoUpdateSchema,
)
from .serializers import CategorySerializer, CommentSerializer, LabelSerializer, RegisterSerializer, TaskSerializer, TodoSerializer
from .services import CategoryService, CommentService, LabelService, ServiceValidationError, TaskService, TodoService, UserService
from .validation import build_schema


def integrity_error_response(error: IntegrityError):
    return Response({"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST)


def service_error_response(error: ServiceValidationError):
    return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=RegisterSerializer, responses=RegisterSerializer)
    def post(self, request):
        data = build_schema(RegisterCreateSchema, request.data)
        try:
            validate_password(data.password)
            user = UserService.register_user(data)
        except DjangoValidationError as error:
            return Response({"password": list(error.messages)}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as error:
            return integrity_error_response(error)
        return Response(user_to_dict(user), status=status.HTTP_201_CREATED)


class PydanticViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def list_response(self, queryset, presenter):
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response([presenter(item) for item in page])
        return Response([presenter(item) for item in queryset])

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(PydanticViewSet):
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Category.objects.none()
        return CategoryService.get_categories_for_user(self.request.user)

    @extend_schema(responses=CategorySerializer(many=True))
    def list(self, request):
        return self.list_response(self.get_queryset(), category_to_dict)

    @extend_schema(responses=CategorySerializer)
    def retrieve(self, request, pk=None):
        return Response(category_to_dict(self.get_object()))

    @extend_schema(request=CategorySerializer, responses=CategorySerializer)
    def create(self, request):
        data = build_schema(CategoryCreateSchema, request.data)
        try:
            category = CategoryService.create_category(request.user, data)
        except IntegrityError as error:
            return integrity_error_response(error)
        return Response(category_to_dict(category), status=status.HTTP_201_CREATED)

    @extend_schema(request=CategorySerializer, responses=CategorySerializer)
    def update(self, request, pk=None):
        data = build_schema(CategoryUpdateSchema, request.data)
        try:
            category = CategoryService.update_category(self.get_object(), data)
        except IntegrityError as error:
            return integrity_error_response(error)
        return Response(category_to_dict(category))

    @extend_schema(request=CategorySerializer, responses=CategorySerializer)
    def partial_update(self, request, pk=None):
        return self.update(request, pk)


class LabelViewSet(PydanticViewSet):
    serializer_class = LabelSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "color"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Label.objects.none()
        return LabelService.get_labels_for_user(self.request.user)

    @extend_schema(responses=LabelSerializer(many=True))
    def list(self, request):
        return self.list_response(self.get_queryset(), label_to_dict)

    @extend_schema(responses=LabelSerializer)
    def retrieve(self, request, pk=None):
        return Response(label_to_dict(self.get_object()))

    @extend_schema(request=LabelSerializer, responses=LabelSerializer)
    def create(self, request):
        data = build_schema(LabelCreateSchema, request.data)
        try:
            label = LabelService.create_label(request.user, data)
        except IntegrityError as error:
            return integrity_error_response(error)
        return Response(label_to_dict(label), status=status.HTTP_201_CREATED)

    @extend_schema(request=LabelSerializer, responses=LabelSerializer)
    def update(self, request, pk=None):
        data = build_schema(LabelUpdateSchema, request.data)
        try:
            label = LabelService.update_label(self.get_object(), data)
        except IntegrityError as error:
            return integrity_error_response(error)
        return Response(label_to_dict(label))

    @extend_schema(request=LabelSerializer, responses=LabelSerializer)
    def partial_update(self, request, pk=None):
        return self.update(request, pk)


class TaskViewSet(PydanticViewSet):
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        "status": ["exact"],
        "priority": ["exact"],
        "category": ["exact"],
        "labels": ["exact"],
        "deadline": ["exact", "gte", "lte", "isnull"],
    }
    search_fields = ["title", "description"]
    ordering_fields = ["deadline", "status", "priority", "created_at", "updated_at", "title"]
    ordering = ["deadline", "-created_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Task.objects.none()
        return TaskService.get_tasks_for_user(self.request.user)

    def get_pydantic_payload(self, request):
        payload = request.data.copy()
        if "category" in payload:
            payload["category_id"] = payload.pop("category")
        return payload

    @extend_schema(responses=TaskSerializer(many=True))
    def list(self, request):
        return self.list_response(self.get_queryset(), task_to_dict)

    @extend_schema(responses=TaskSerializer)
    def retrieve(self, request, pk=None):
        return Response(task_to_dict(self.get_object()))

    @extend_schema(request=TaskSerializer, responses=TaskSerializer)
    def create(self, request):
        data = build_schema(TaskCreateSchema, self.get_pydantic_payload(request))
        try:
            task = TaskService.create_task(request.user, data)
        except ServiceValidationError as error:
            return service_error_response(error)
        return Response(task_to_dict(task), status=status.HTTP_201_CREATED)

    @extend_schema(request=TaskSerializer, responses=TaskSerializer)
    def update(self, request, pk=None):
        data = build_schema(TaskUpdateSchema, self.get_pydantic_payload(request))
        try:
            task = TaskService.update_task(request.user, self.get_object(), data)
        except ServiceValidationError as error:
            return service_error_response(error)
        return Response(task_to_dict(task))

    @extend_schema(request=TaskSerializer, responses=TaskSerializer)
    def partial_update(self, request, pk=None):
        return self.update(request, pk)

    @extend_schema(responses=TaskSerializer)
    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = TaskService.complete_task(self.get_object())
        return Response(task_to_dict(task), status=status.HTTP_200_OK)

    @extend_schema(responses=TaskSerializer)
    @action(detail=True, methods=["post"])
    def reopen(self, request, pk=None):
        task = TaskService.reopen_task(self.get_object())
        return Response(task_to_dict(task), status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        return Response(TaskService.get_stats(self.filter_queryset(self.get_queryset())))


class CommentViewSet(PydanticViewSet):
    serializer_class = CommentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["task"]
    search_fields = ["text"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["created_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Comment.objects.none()
        return CommentService.get_comments_for_user(self.request.user)

    def get_pydantic_payload(self, request):
        payload = request.data.copy()
        if "task" in payload:
            payload["task_id"] = payload.pop("task")
        return payload

    @extend_schema(responses=CommentSerializer(many=True))
    def list(self, request):
        return self.list_response(self.get_queryset(), comment_to_dict)

    @extend_schema(responses=CommentSerializer)
    def retrieve(self, request, pk=None):
        return Response(comment_to_dict(self.get_object()))

    @extend_schema(request=CommentSerializer, responses=CommentSerializer)
    def create(self, request):
        data = build_schema(CommentCreateSchema, self.get_pydantic_payload(request))
        try:
            comment = CommentService.create_comment(request.user, data)
        except ServiceValidationError as error:
            return service_error_response(error)
        return Response(comment_to_dict(comment), status=status.HTTP_201_CREATED)

    @extend_schema(request=CommentSerializer, responses=CommentSerializer)
    def update(self, request, pk=None):
        data = build_schema(CommentUpdateSchema, self.get_pydantic_payload(request))
        try:
            comment = CommentService.update_comment(request.user, self.get_object(), data)
        except ServiceValidationError as error:
            return service_error_response(error)
        return Response(comment_to_dict(comment))

    @extend_schema(request=CommentSerializer, responses=CommentSerializer)
    def partial_update(self, request, pk=None):
        return self.update(request, pk)


class TodoViewSet(PydanticViewSet):
    serializer_class = TodoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_completed"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "title"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Todo.objects.none()
        return TodoService.get_todos_for_user(self.request.user)

    @extend_schema(responses=TodoSerializer(many=True))
    def list(self, request):
        return self.list_response(self.get_queryset(), todo_to_dict)

    @extend_schema(responses=TodoSerializer)
    def retrieve(self, request, pk=None):
        return Response(todo_to_dict(self.get_object()))

    @extend_schema(request=TodoSerializer, responses=TodoSerializer)
    def create(self, request):
        data = build_schema(TodoCreateSchema, request.data)
        todo = TodoService.create_todo(request.user, data)
        return Response(todo_to_dict(todo), status=status.HTTP_201_CREATED)

    @extend_schema(request=TodoSerializer, responses=TodoSerializer)
    def update(self, request, pk=None):
        data = build_schema(TodoUpdateSchema, request.data)
        todo = TodoService.update_todo(self.get_object(), data)
        return Response(todo_to_dict(todo))

    @extend_schema(request=TodoSerializer, responses=TodoSerializer)
    def partial_update(self, request, pk=None):
        return self.update(request, pk)

    @extend_schema(responses=TodoSerializer)
    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        todo = TodoService.mark_as_completed(self.get_object())
        return Response(todo_to_dict(todo), status=status.HTTP_200_OK)

    @extend_schema(responses=TodoSerializer)
    @action(detail=True, methods=["post"])
    def uncomplete(self, request, pk=None):
        todo = TodoService.mark_as_uncompleted(self.get_object())
        return Response(todo_to_dict(todo), status=status.HTTP_200_OK)
