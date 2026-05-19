def user_to_dict(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }


def todo_to_dict(todo):
    return {
        "id": todo.id,
        "title": todo.title,
        "description": todo.description,
        "is_completed": todo.is_completed,
        "user": todo.user_id,
        "created_at": todo.created_at,
        "updated_at": todo.updated_at,
    }


def category_to_dict(category):
    return {
        "id": category.id,
        "name": category.name,
        "user": category.user_id,
        "created_at": category.created_at,
    }


def label_to_dict(label):
    return {
        "id": label.id,
        "name": label.name,
        "color": label.color,
        "user": label.user_id,
        "created_at": label.created_at,
    }


def task_to_dict(task):
    category = task.category
    status = task.status.value if hasattr(task.status, "value") else task.status
    priority = task.priority.value if hasattr(task.priority, "value") else task.priority
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "deadline": task.deadline,
        "status": status,
        "status_display": task.get_status_display(),
        "priority": priority,
        "priority_display": task.get_priority_display(),
        "user": task.user_id,
        "category": task.category_id,
        "category_detail": category_to_dict(category) if category else None,
        "labels": [label_to_dict(label) for label in task.labels.all()],
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


def comment_to_dict(comment):
    return {
        "id": comment.id,
        "task": comment.task_id,
        "user": comment.user_id,
        "text": comment.text,
        "created_at": comment.created_at,
        "updated_at": comment.updated_at,
    }
