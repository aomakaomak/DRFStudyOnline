from materials.apps import MaterialsConfig
from rest_framework.routers import DefaultRouter
from django.urls import path

from materials.views import CourseViewSet, LessonUpdateAPIView, LessonDestroyAPIView, LessonRetrieveAPIView, LessonListAPIView, LessonCreateAPIView
app_name = MaterialsConfig.name

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='courses')

urlpatterns = [
    path('lessons/create/', LessonCreateAPIView.as_view(), name='lesson-create'),
    path('lessons/', LessonListAPIView.as_view(), name='lessons-list'),
    path('lessons/<int:pk>/', LessonRetrieveAPIView.as_view(), name='lesson-get'),
    path('lessons/update/<int:pk>/', LessonUpdateAPIView.as_view(), name='lesson-update'),
    path('lessons/delete/<int:pk>/', LessonDestroyAPIView.as_view(), name='lesson-delete'),
] + router.urls