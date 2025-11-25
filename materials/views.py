from django.shortcuts import get_object_or_404

from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.models import Course, Lesson, Subscription
from materials.paginators import MaterialsPaginator
from materials.permissions import IsModerator, IsOwner
from materials.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    pagination_class = MaterialsPaginator

    def get_permissions(self):
        if self.action == "create" or self.action == "destroy":
            self.permission_classes = [IsAuthenticated, IsOwner]
        elif (
            self.action == "list"
            or self.action == "update"
            or self.action == "retrieve"
        ):
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        new_course = serializer.save()
        new_course.owner = self.request.user
        new_course.save()


class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        new_lesson = serializer.save()
        new_lesson.owner = self.request.user
        new_lesson.save()


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsModerator]
    pagination_class = MaterialsPaginator


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]


class LessonUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]


class SubscriptionAPIView(APIView):
    """
    POST /api/subscriptions/
    body: {"course_id": <id курса>}

    Если подписка была — удаляем и возвращаем message="подписка удалена".
    Если подписки не было — создаём и возвращаем message="подписка добавлена".
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")

        if course_id is None:
            return Response(
                {"detail": "Не передан параметр course_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        course_item = get_object_or_404(Course, id=course_id)

        subs_qs = Subscription.objects.filter(user=user, course=course_item)

        if subs_qs.exists():
            # Подписка существует — удаляем все на всякий случай
            subs_qs.delete()
            message = "подписка удалена"
        else:
            # Подписки нет — создаём
            Subscription.objects.create(
                user=user,
                course=course_item,
                title=f"Подписка на курс {course_item.title}"
            )
            message = "подписка добавлена"

        return Response({"message": message}, status=status.HTTP_200_OK)
