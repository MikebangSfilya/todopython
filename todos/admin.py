from django.contrib import admin

from .models import Category, Comment, Label, Task, TaskLabel, Todo


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "is_completed", "created_at", "updated_at")
    list_filter = ("is_completed", "user", "created_at")
    search_fields = ("title", "description")
    ordering = ("-created_at",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "created_at")
    list_filter = ("user", "created_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color", "user", "created_at")
    list_filter = ("user", "created_at")
    search_fields = ("name", "color")
    ordering = ("name",)


class TaskLabelInline(admin.TabularInline):
    model = TaskLabel
    extra = 1


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "category", "status", "priority", "deadline", "created_at")
    list_filter = ("status", "priority", "category", "user", "deadline")
    search_fields = ("title", "description")
    ordering = ("deadline", "-created_at")
    inlines = [TaskLabelInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "task", "user", "created_at", "updated_at")
    list_filter = ("user", "created_at")
    search_fields = ("text", "task__title")
    ordering = ("created_at",)


@admin.register(TaskLabel)
class TaskLabelAdmin(admin.ModelAdmin):
    list_display = ("id", "task", "label", "created_at")
    list_filter = ("label", "created_at")
    search_fields = ("task__title", "label__name")
