from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q

User = get_user_model()


@shared_task
def deactivate_inactive_users() -> str:
    """
    Периодическая задача:
    Блокирует пользователей, которые не заходили более 30 дней.
    Условие: last_login < (now - 30 дней) ИЛИ last_login IS NULL.
    """
    now = timezone.now()
    cutoff = now - timedelta(days=30)

    inactive_qs = User.objects.filter(
        is_active=True
    ).filter(
        Q(last_login__lt=cutoff) | Q(last_login__isnull=True)
    )

    inactive_qs = inactive_qs.filter(is_superuser=False)

    updated_count = inactive_qs.update(is_active=False)

    return f"Деактивировано пользователей: {updated_count}"
