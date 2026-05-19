from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, CommentViewSet, LabelViewSet, RegisterView, TaskViewSet, TodoViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"labels", LabelViewSet, basename="label")
router.register(r"comments", CommentViewSet, basename="comment")
router.register(r"todos", TodoViewSet, basename="todo")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("", include(router.urls)),
]
