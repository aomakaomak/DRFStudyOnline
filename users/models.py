from django.db import models
from django.contrib.auth.models import AbstractUser

from materials.models import Course, Lesson


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Почта")
    phone_number = models.CharField(
        max_length=15, blank=True, null=True, verbose_name="Номер телефона"
    )
    city = models.CharField(max_length=50, verbose_name="Город", null=True, blank=True)
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name="Аватар"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"


class Payment(models.Model):
    CASH = "cash"
    TRANSFER = "transfer"

    PAYMENT_METHOD_CHOICES = [
        (CASH, "наличные"),
        (TRANSFER, "банковский перевод"),
    ]

    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_CANCELED = "canceled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "ожидает оплаты"),
        (STATUS_PAID, "оплачен"),
        (STATUS_CANCELED, "отменён"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
    )
    payment_date = models.DateField(verbose_name="Дата оплаты")
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Оплаченный курс",
        blank=True,
        null=True,
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Оплаченный урок",
        blank=True,
        null=True,
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Сумма оплаты"
    )
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name="Метод оплаты"
    )

    # --- Stripe-поля ---
    stripe_product_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID продукта в Stripe",
    )
    stripe_price_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID цены в Stripe",
    )
    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID сессии Checkout в Stripe",
    )
    payment_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Ссылка на оплату (Stripe Checkout)",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name="Статус платежа",
    )

    def __str__(self):
        return f"Платеж #{self.id} от {self.user} на сумму {self.amount}"

    class Meta:
        verbose_name = "платеж"
        verbose_name_plural = "платежи"