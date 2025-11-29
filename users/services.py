import stripe
from django.conf import settings

from materials.models import Course

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product_for_course(course: Course) -> str:
    """
    Создаёт продукт в Stripe для конкретного курса.
    Возвращает product.id
    """
    product = stripe.Product.create(
        name=course.title,
        description=course.description or "",
    )
    return product["id"]


def create_stripe_price_for_course(course: Course, product_id: str) -> str:
    """
    Создаёт price в Stripe для курса.
    Цена передаётся в копейках (умножаем на 100).
    Возвращает price.id
    """
    unit_amount = int(course.price * 100)

    price = stripe.Price.create(
        unit_amount=unit_amount,
        currency="rub",
        product=product_id,
    )
    return price["id"]


def create_stripe_checkout_session(price_id: str, success_url: str, cancel_url: str) -> dict:
    """
    Создаёт Checkout Session и возвращает словарь с id и url.
    """
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        success_url=success_url,
        cancel_url=cancel_url,
    )

    return {
        "id": session["id"],
        "url": session["url"],
    }


def retrieve_checkout_session(session_id: str) -> dict:
    """
    Получить данные по сессии (для проверки статуса).
    """
    session = stripe.checkout.Session.retrieve(session_id)
    return session
