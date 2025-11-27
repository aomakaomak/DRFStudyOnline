from django.utils import timezone
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, status
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.models import Course
from users.models import User, Payment
from users.permissions import IsOwnerOrReadOnly
from users.serializers import (
    UserSerializer,
    PaymentSerializer,
    PaymentCreateStripeSerializer,
)
from users.services import (
    create_stripe_product_for_course,
    create_stripe_price_for_course,
    create_stripe_checkout_session,
    retrieve_checkout_session,
)
from django.conf import settings


class UserViewSet(viewsets.ModelViewSet):

    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        else:
            permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

        return [permission() for permission in permission_classes]


class PaymentListAPIView(generics.ListAPIView):

    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ("course", "lesson", "payment_method")
    ordering_fields = ("payment_date",)


class CreateStripeCheckoutSessionAPIView(APIView):
    """
    POST /users/payments/create-checkout-session/
    body: {"course_id": <id курса>}

    1. Проверяем курс.
    2. Создаём product, price, checkout session в Stripe.
    3. Создаём Payment в БД.
    4. Возвращаем данные платежа с ссылкой payment_url.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = PaymentCreateStripeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course_id = serializer.validated_data["course_id"]
        user = request.user

        course = get_object_or_404(Course, id=course_id)

        # 1. Продукт в Stripe
        stripe_product_id = create_stripe_product_for_course(course)

        # 2. Цена в Stripe
        stripe_price_id = create_stripe_price_for_course(course, stripe_product_id)

        # 3. Сессия Checkout в Stripe
        success_url = f"{settings.SITE_URL}/payments/success/"
        cancel_url = f"{settings.SITE_URL}/payments/cancel/"

        session_data = create_stripe_checkout_session(
            price_id=stripe_price_id,
            success_url=success_url,
            cancel_url=cancel_url,
        )

        stripe_session_id = session_data["id"]
        payment_url = session_data["url"]

        # 4. Создаём Payment у себя
        payment = Payment.objects.create(
            user=user,
            payment_date=timezone.now().date(),
            course=course,
            lesson=None,
            amount=course.price,
            payment_method=Payment.TRANSFER,  # как "безналичный перевод"/эквайринг
            stripe_product_id=stripe_product_id,
            stripe_price_id=stripe_price_id,
            stripe_session_id=stripe_session_id,
            payment_url=payment_url,
            status=Payment.STATUS_PENDING,
        )

        output_serializer = PaymentSerializer(payment)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class PaymentStripeStatusAPIView(APIView):
    """
    GET /users/payments/<int:pk>/status/

    По нашему payment.id смотрим stripe_session_id и
    тянем статус из Stripe.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        payment = get_object_or_404(Payment, pk=pk, user=request.user)

        if not payment.stripe_session_id:
            return Response(
                {"detail": "Для данного платежа не создана Stripe-сессия."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session = retrieve_checkout_session(payment.stripe_session_id)
        stripe_status = session.get("payment_status")  # 'paid', 'unpaid', 'no_payment_required'

        return Response(
            {
                "payment_id": payment.id,
                "local_status": payment.status,
                "stripe_status": stripe_status,
            },
            status=status.HTTP_200_OK,
        )