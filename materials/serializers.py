from rest_framework import serializers

from materials.models import Course, Lesson, Subscription
from materials.validators import LinkValidator


class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = "__all__"

        validators = [
            LinkValidator(field='link')
        ]


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"

    def get_lessons_count(self, instance):
        return instance.lessons.count()

    def get_is_subscribed(self, instance):
        request = self.context.get('request')
        if request is None:
            return False

        user = request.user
        if user.is_anonymous:
            return False

        return instance.subscriptions.filter(user=user).exists()


