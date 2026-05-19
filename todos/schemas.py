from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .models import Task


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RegisterCreateSchema(StrictBaseModel):
    username: str
    email: str = ""
    password: str

    @field_validator("username", "password")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty.")
        return value


class CategoryCreateSchema(StrictBaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Category name cannot be empty.")
        return value


class CategoryUpdateSchema(StrictBaseModel):
    name: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Category name cannot be empty.")
        return value


class LabelCreateSchema(StrictBaseModel):
    name: str
    color: str = ""

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Label name cannot be empty.")
        return value

    @field_validator("color")
    @classmethod
    def validate_color(cls, value: str) -> str:
        return value.strip()


class LabelUpdateSchema(StrictBaseModel):
    name: str | None = None
    color: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Label name cannot be empty.")
        return value

    @field_validator("color")
    @classmethod
    def validate_color(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else value


class TaskBaseSchema(StrictBaseModel):
    title: str | None = None
    description: str | None = None
    deadline: datetime | None = None
    status: Literal[Task.Status.TODO, Task.Status.IN_PROGRESS, Task.Status.DONE] | None = None
    priority: Literal[Task.Priority.LOW, Task.Priority.MEDIUM, Task.Priority.HIGH] | None = None
    category_id: int | None = None
    label_ids: list[int] | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Task title cannot be empty.")
        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else value

    @field_validator("label_ids")
    @classmethod
    def validate_label_ids(cls, value: list[int] | None) -> list[int] | None:
        if value is None:
            return value
        return list(dict.fromkeys(value))


class TaskCreateSchema(TaskBaseSchema):
    title: str
    description: str = ""
    status: Literal[Task.Status.TODO, Task.Status.IN_PROGRESS, Task.Status.DONE] = Task.Status.TODO
    priority: Literal[Task.Priority.LOW, Task.Priority.MEDIUM, Task.Priority.HIGH] = Task.Priority.MEDIUM
    label_ids: list[int] = Field(default_factory=list)


class TaskUpdateSchema(TaskBaseSchema):
    pass


class CommentCreateSchema(StrictBaseModel):
    task_id: int
    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Comment text cannot be empty.")
        return value


class CommentUpdateSchema(StrictBaseModel):
    task_id: int | None = None
    text: str | None = None

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Comment text cannot be empty.")
        return value


class TodoCreateSchema(StrictBaseModel):
    title: str
    description: str = ""
    is_completed: bool = False

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Title cannot be empty.")
        return value


class TodoUpdateSchema(StrictBaseModel):
    title: str | None = None
    description: str | None = None
    is_completed: bool | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Title cannot be empty.")
        return value
