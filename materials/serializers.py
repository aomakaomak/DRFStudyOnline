from rest_framework import serializers

from materials.models import Course, Lesson
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

    class Meta:
        model = Course
        fields = "__all__"

    def get_lessons_count(self, instance):
        return instance.lessons.count()
