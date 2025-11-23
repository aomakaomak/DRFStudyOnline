from rest_framework import serializers

from users.models import User, Payment


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = "__all__"


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

        request = self.context.get('request', None)
        user = getattr(request, 'user', None)

        if user and (user.is_staff or user.is_superuser):
            return data

        if not user or user.pk != instance.pk:
            data.pop('last_name', None)
            data.pop('payments', None)

        return data
