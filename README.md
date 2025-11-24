# Django Courses API

Небольшой учебный проект на **Django** и **Django REST Framework** для управления курсами и уроками.  
Проект демонстрирует работу с моделями, связями `One-to-Many`, пользовательскими правами доступа и классами представлений DRF (`ViewSet` и generic CBV).

## Возможности

- Создание и управление **курсами**
  - название
  - текстовое описание
  - превью (изображение)
  - владелец курса (пользователь)
- Создание и управление **уроками**, привязанными к курсу
  - название
  - описание
  - превью (изображение)
  - ссылка на видео
  - принадлежность к курсу
  - владелец урока
- Гибкая система прав:
  - **модератор** (группа `moderator`)
  - **владелец** объекта (курс/урок)
- REST API на базе Django REST Framework

---

## Стек технологий

- Python
- Django
- Django REST Framework
- Django auth/groups (для ролей модератора и владельца)
- Pillow (для работы с ImageField, при необходимости)

> Конкретные версии зависят от вашего `requirements.txt`.

---

## Структура основных файлов

### Модели (`materials/models.py`)

```python
from django.db import models
from django.conf import settings

class Course(models.Model):
    title = models.CharField(max_length=150, verbose_name='название')
    description = models.TextField(verbose_name='описание')
    preview = models.ImageField(upload_to="courses/previews/", blank=True, null=True, verbose_name="Превью")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='courses')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'курс'
        verbose_name_plural = 'курсы'


class Lesson(models.Model):
    title = models.CharField(max_length=150, verbose_name='название')
    description = models.TextField(verbose_name='описание')
    preview = models.ImageField(upload_to="lessons/previews/", blank=True, null=True, verbose_name="Превью")
    link = models.URLField(max_length=150, verbose_name='ссылка на видео')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name='Курс')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='lessons')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'урок'
        verbose_name_plural = 'уроки'
```

### Права доступа (`materials/permissions.py`)

```python
from rest_framework.permissions import BasePermission

class IsModerator(BasePermission):

    def has_permission(self, request, view):
        if request.user.groups.filter(name='moderator').exists():
            return True
        return False


class IsOwner(BasePermission):

    def has_permission(self, request, view):
        return request.user == view.get_object().owner
```

> Обратите внимание: для корректной работы `IsOwner` объект должен быть доступен через `view.get_object()` (это делает DRF, когда вы используете детальные представления/GenericAPIView/ModelViewSet).

### Сериализаторы (`materials/serializers.py`)

```python
from rest_framework import serializers

from materials.models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = '__all__'

    def get_lessons_count(self, instance):
        return instance.lessons.count()
```

### Вьюхи (`materials/views.py`)

```python
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated

from materials.models import Course, Lesson
from materials.permissions import IsModerator, IsOwner
from materials.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()

    def get_permissions(self):
        if self.action == 'create' or self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, IsOwner]
        elif self.action == 'list' or self.action == 'update' or self.action == 'retrieve':
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
```

---

## Настройка и запуск проекта локально

### 1. Клонировать репозиторий

```bash
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>.git
cd <ИМЯ_ПРОЕКТА>
```

### 2. Создать и активировать виртуальное окружение

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

> Если файла `requirements.txt` нет — сформируйте его сами командой:`pip freeze > requirements.txt` после установки всех нужных пакетов (Django, djangorestframework и т.д.).

### 4. Применить миграции

```bash
python manage.py migrate
```

### 5. Создать суперпользователя

```bash
python manage.py createsuperuser
```

Следуйте инструкциям в консоли.

### 6. Настроить статику и медиа (минимально)

В `settings.py` должны быть настроены параметры для медиа-файлов, например:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

Не забудьте добавить раздачу медиа в `urls.py` (в режиме DEBUG).

### 7. Запустить сервер разработки

```bash
python manage.py runserver
```

По умолчанию сервер будет доступен по адресу `http://127.0.0.1:8000/`.

---

## Подключение вьюх к URL

Точные URL-адреса зависят от вашего `urls.py`. Ниже — пример, как можно подключить указанные классы представлений.

### Пример через router для `CourseViewSet`

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from materials.views import (
    CourseViewSet,
    LessonCreateAPIView,
    LessonListAPIView,
    LessonRetrieveAPIView,
    LessonUpdateAPIView,
    LessonDestroyAPIView,
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')

urlpatterns = [
    path('api/', include(router.urls)),

    path('api/lessons/', LessonListAPIView.as_view(), name='lesson-list'),
    path('api/lessons/create/', LessonCreateAPIView.as_view(), name='lesson-create'),
    path('api/lessons/<int:pk>/', LessonRetrieveAPIView.as_view(), name='lesson-detail'),
    path('api/lessons/<int:pk>/update/', LessonUpdateAPIView.as_view(), name='lesson-update'),
    path('api/lessons/<int:pk>/delete/', LessonDestroyAPIView.as_view(), name='lesson-delete'),
]
```

> Это пример. В своём проекте вы можете использовать любые пути, главное — сохранить связь с соответствующими классами представлений.

---

## Модель прав доступа

### Роли

- **Аутентифицированный пользователь** (`IsAuthenticated`)
- **Модератор** — пользователь, состоящий в группе `moderator`
- **Владелец** — пользователь, который записан в поле `owner` у курса/урока

### CourseViewSet

- `create`, `destroy` — только **аутентифицированный владелец** (`IsAuthenticated`, `IsOwner`)
- `list`, `update`, `retrieve` — **модератор или владелец** (`IsAuthenticated`, `IsModerator | IsOwner`)

### LessonAPIView

- Создание урока (`LessonCreateAPIView`) — любой **аутентифицированный пользователь**
- Список уроков (`LessonListAPIView`) — только **модератор**
- Просмотр, обновление урока (`LessonRetrieveAPIView`, `LessonUpdateAPIView`) — **модератор или владелец**
- Удаление урока (`LessonDestroyAPIView`) — только **владелец**

---

## Как протестировать API

1. Запускаем сервер:

   ```bash
   python manage.py runserver
   ```

2. Заходим в браузер по адресу ваших эндпоинтов (например, `http://127.0.0.1:8000/api/courses/` и т.д.) — DRF предоставляет удобный web-интерфейс.
3. Авторизуемся (Basic Auth / Session Auth / Token Auth — в зависимости от вашей настройки REST_FRAMEWORK).
4. Проверяем:
   - создание курса/урока;
   - просмотр списка курсов и уроков;
   - обновление и удаление объектов в зависимости от прав пользователя;
   - работу групп и владельцев.

---

## Возможные доработки

- Добавить пагинацию, фильтрацию и поиск по курсам и урокам.
- Вынести настройки прав доступа в отдельные mixin-классы.
- Добавить JWT-аутентификацию через `djangorestframework-simplejwt`.
- Подключить Swagger / drf-spectacular для документации API.
- Написать unit-тесты для моделей, сериализаторов и вьюх.

---

## Лицензия

Вы можете использовать и модифицировать этот проект в учебных и рабочих целях на своё усмотрение (если не предусмотрено иное в вашем репозитории).
