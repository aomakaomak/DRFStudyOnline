from rest_framework import serializers

from users.models import User, Payment
from materials.models import Course


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = (
            "id",
            "user",
            "payment_date",
            "amount",
            "payment_method",
            "stripe_product_id",
            "stripe_price_id",
            "stripe_session_id",
            "payment_url",
            "status",
        )


class PaymentCreateStripeSerializer(serializers.Serializer):
    """
    Используется только для создания Stripe Checkout Session.
    Вход: id курса.
    """
    course_id = serializers.IntegerField()

    def validate_course_id(self, value):
        try:
            course = Course.objects.get(id=value)
        except Course.DoesNotExist:
            raise serializers.ValidationError("Курс с таким id не найден.")
        if course.price <= 0:
            raise serializers.ValidationError("У курса должна быть положительная цена.")
        return value


class UserSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get("request", None)
        user = getattr(request, "user", None)

        if user and (user.is_staff or user.is_superuser):
            return data

        if not user or user.pk != instance.pk:
            data.pop("last_name", None)
            data.pop("payments", None)

        return data
