from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from materials.models import Course, Subscription


@shared_task
def send_course_update_email(course_id: int) -> str:
    """
    Асинхронная задача рассылки писем подписчикам курса
    при обновлении материалов курса.
    """
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return f"Курс с id={course_id} не найден"

    # Все подписки на этот курс
    subscriptions = Subscription.objects.filter(course=course).select_related("user")

    # Собираем email'ы подписчиков
    recipient_list = [
        sub.user.email
        for sub in subscriptions
        if sub.user and sub.user.email
    ]

    if not recipient_list:
        return f"Нет подписчиков с email для курса id={course_id}"

    subject = f"Обновление материалов курса «{course.title}»"
    message = (
        f"Курс «{course.title}» был обновлён.\n\n"
        f"Зайдите в свой личный кабинет, чтобы ознакомиться с новыми материалами."
    )

    # Отправитель — используем EMAIL_HOST_USER или DEFAULT_FROM_EMAIL
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or getattr(settings, "EMAIL_HOST_USER", None)

    if not from_email:
        # Если не настроен FROM, всё равно возвращаем инфо
        return "Не настроен DEFAULT_FROM_EMAIL или EMAIL_HOST_USER в settings.py"

    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        fail_silently=False,
    )

    return f"Отправлено {len(recipient_list)} писем подписчикам курса id={course_id}"
