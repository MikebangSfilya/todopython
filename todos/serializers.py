from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Category, Comment, Label, Task, Todo


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = get_user_model()
        fields = ["id", "username", "email", "password"]
        read_only_fields = ["id"]


class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ["id", "title", "description", "is_completed", "user", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "user", "created_at"]
        read_only_fields = ["id", "user", "created_at"]


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ["id", "name", "color", "user", "created_at"]
        read_only_fields = ["id", "user", "created_at"]


class TaskSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source="category", read_only=True)
    labels = LabelSerializer(many=True, read_only=True)
    status_display = serializers.CharField(read_only=True)
    priority_display = serializers.CharField(read_only=True)
    label_ids = serializers.PrimaryKeyRelatedField(
        queryset=Label.objects.none(),
        many=True,
        write_only=True,
        required=False,
        source="labels",
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "deadline",
            "status",
            "status_display",
            "priority",
            "priority_display",
            "user",
            "category",
            "category_detail",
            "labels",
            "label_ids",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "task", "user", "text", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]
