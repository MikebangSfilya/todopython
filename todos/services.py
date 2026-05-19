from typing import Optional

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.utils import timezone

from .models import Category, Comment, Label, Task, Todo
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


class ServiceValidationError(Exception):
    def __init__(self, detail):
        self.detail = detail
        super().__init__(str(detail))


def apply_updates(instance, data: dict, update_fields: list[str]):
    changed_fields = []
    for field in update_fields:
        if field not in data:
            continue
        setattr(instance, field, data[field])
        changed_fields.append(field)

    if changed_fields:
        if hasattr(instance, "updated_at") and "updated_at" not in changed_fields:
            changed_fields.append("updated_at")
        instance.save(update_fields=changed_fields)
    return instance


class UserService:
    @staticmethod
    def register_user(data: RegisterCreateSchema):
        return get_user_model().objects.create_user(**data.model_dump())


class CategoryService:
    @staticmethod
    def get_categories_for_user(user) -> QuerySet[Category]:
        if user.is_superuser:
            return Category.objects.all()
        return Category.objects.filter(user=user)

    @staticmethod
    def create_category(user, data: CategoryCreateSchema) -> Category:
        return Category.objects.create(user=user, **data.model_dump())

    @staticmethod
    def update_category(category: Category, data: CategoryUpdateSchema) -> Category:
        return apply_updates(category, data.model_dump(exclude_unset=True), ["name"])


class LabelService:
    @staticmethod
    def get_labels_for_user(user) -> QuerySet[Label]:
        if user.is_superuser:
            return Label.objects.all()
        return Label.objects.filter(user=user)

    @staticmethod
    def create_label(user, data: LabelCreateSchema) -> Label:
        return Label.objects.create(user=user, **data.model_dump())

    @staticmethod
    def update_label(label: Label, data: LabelUpdateSchema) -> Label:
        return apply_updates(label, data.model_dump(exclude_unset=True), ["name", "color"])


class TaskService:
    @staticmethod
    def get_tasks_for_user(user) -> QuerySet[Task]:
        queryset = Task.objects.select_related("category", "user").prefetch_related("labels")
        if user.is_superuser:
            return queryset.distinct()
        return queryset.filter(user=user).distinct()

    @staticmethod
    def get_available_categories(user) -> QuerySet[Category]:
        if user.is_superuser:
            return Category.objects.all()
        return Category.objects.filter(user=user)

    @staticmethod
    def get_available_labels(user) -> QuerySet[Label]:
        if user.is_superuser:
            return Label.objects.all()
        return Label.objects.filter(user=user)

    @staticmethod
    def validate_category(user, category_id: int | None) -> None:
        if category_id is None:
            return
        if not TaskService.get_available_categories(user).filter(id=category_id).exists():
            raise ServiceValidationError({"category": ["Category does not exist."]})

    @staticmethod
    def validate_labels(user, label_ids: list[int]) -> None:
        existing_count = TaskService.get_available_labels(user).filter(id__in=label_ids).count()
        if existing_count != len(label_ids):
            raise ServiceValidationError({"label_ids": ["One or more labels do not exist."]})

    @staticmethod
    def create_task(user, data: TaskCreateSchema) -> Task:
        TaskService.validate_category(user, data.category_id)
        TaskService.validate_labels(user, data.label_ids)
        payload = data.model_dump(exclude={"label_ids", "category_id"})
        payload["category_id"] = data.category_id
        task = Task.objects.create(user=user, **payload)
        task.labels.set(TaskService.get_available_labels(user).filter(id__in=data.label_ids))
        return task

    @staticmethod
    def update_task(user, task: Task, data: TaskUpdateSchema) -> Task:
        if "category_id" in data.model_fields_set:
            TaskService.validate_category(user, data.category_id)
        if data.label_ids is not None:
            TaskService.validate_labels(user, data.label_ids)

        payload = data.model_dump(exclude_unset=True, exclude={"label_ids", "category_id"})
        if "category_id" in data.model_fields_set:
            payload["category_id"] = data.category_id

        task = apply_updates(
            task,
            payload,
            ["title", "description", "deadline", "status", "priority", "category_id"],
        )
        if data.label_ids is not None:
            task.labels.set(TaskService.get_available_labels(user).filter(id__in=data.label_ids))
        return task

    @staticmethod
    def complete_task(task: Task) -> Task:
        task.status = Task.Status.DONE
        task.save(update_fields=["status", "updated_at"])
        return task

    @staticmethod
    def reopen_task(task: Task) -> Task:
        task.status = Task.Status.TODO
        task.save(update_fields=["status", "updated_at"])
        return task

    @staticmethod
    def get_stats(queryset: QuerySet[Task]) -> dict:
        total = queryset.count()
        completed = queryset.filter(status=Task.Status.DONE).count()
        active = total - completed
        overdue = queryset.exclude(status=Task.Status.DONE).filter(deadline__lt=timezone.now()).count()
        completion_rate = round((completed / total) * 100, 2) if total else 0
        return {
            "total": total,
            "completed": completed,
            "active": active,
            "overdue": overdue,
            "completion_rate": completion_rate,
        }


class CommentService:
    @staticmethod
    def get_comments_for_user(user) -> QuerySet[Comment]:
        queryset = Comment.objects.select_related("task", "user")
        if user.is_superuser:
            return queryset
        return queryset.filter(task__user=user)

    @staticmethod
    def get_available_tasks(user) -> QuerySet[Task]:
        if user.is_superuser:
            return Task.objects.all()
        return Task.objects.filter(user=user)

    @staticmethod
    def validate_task(user, task_id: int | None) -> None:
        if task_id is None:
            return
        if not CommentService.get_available_tasks(user).filter(id=task_id).exists():
            raise ServiceValidationError({"task": ["Task does not exist."]})

    @staticmethod
    def create_comment(user, data: CommentCreateSchema) -> Comment:
        CommentService.validate_task(user, data.task_id)
        return Comment.objects.create(user=user, task_id=data.task_id, text=data.text)

    @staticmethod
    def update_comment(user, comment: Comment, data: CommentUpdateSchema) -> Comment:
        if "task_id" in data.model_fields_set:
            CommentService.validate_task(user, data.task_id)
        payload = data.model_dump(exclude_unset=True)
        return apply_updates(comment, payload, ["task_id", "text"])


class TodoService:
    @staticmethod
    def get_all_todos() -> QuerySet[Todo]:
        return Todo.objects.all()

    @staticmethod
    def get_todos_for_user(user) -> QuerySet[Todo]:
        if user.is_superuser:
            return Todo.objects.all()
        return Todo.objects.filter(user=user)

    @staticmethod
    def get_todo_by_id(todo_id: int) -> Optional[Todo]:
        try:
            return Todo.objects.get(id=todo_id)
        except Todo.DoesNotExist:
            return None

    @staticmethod
    def create_todo(user, data: TodoCreateSchema) -> Todo:
        return Todo.objects.create(user=user, **data.model_dump())

    @staticmethod
    def update_todo(todo: Todo, data: TodoUpdateSchema) -> Todo:
        return apply_updates(todo, data.model_dump(exclude_unset=True), ["title", "description", "is_completed"])

    @staticmethod
    def delete_todo(todo: Todo) -> None:
        todo.delete()

    @staticmethod
    def mark_as_completed(todo: Todo) -> Todo:
        todo.is_completed = True
        todo.save(update_fields=["is_completed", "updated_at"])
        return todo

    @staticmethod
    def mark_as_uncompleted(todo: Todo) -> Todo:
        todo.is_completed = False
        todo.save(update_fields=["is_completed", "updated_at"])
        return todo
