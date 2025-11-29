from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from rest_framework.routers import DefaultRouter
from django.urls import path


from users.views import (
    UserViewSet,
    PaymentListAPIView,
    CreateStripeCheckoutSessionAPIView,
    PaymentStripeStatusAPIView,
)

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("payments/", PaymentListAPIView.as_view(), name="payments-list"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # создание Stripe Checkout Session
    path(
        "payments/create-checkout-session/",
        CreateStripeCheckoutSessionAPIView.as_view(),
        name="payments-create-checkout-session",
    ),

    # проверка статуса платежа через Stripe
    path(
        "payments/<int:pk>/status/",
        PaymentStripeStatusAPIView.as_view(),
        name="payments-stripe-status",
    ),
] + router.urls
