import datetime
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Subscription, UserYaKeys, SubscriptedUser

User = get_user_model()


class CustomCreateUserSerializer(UserCreateSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'id', 'username', 'password', 'first_name', 'last_name', 'email'
        )
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'password': {'required': True},
        }


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'password',
            'first_name',
            'last_name',
        )


class UserYaKeysSerializer(serializers.ModelSerializer):
    """Сериазатор обработки АПИ ключей юзера"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())  # Скрываем поле и назначаем тек. юзера
    FBY_campaign_id = serializers.CharField(max_length=8, min_length=8, required=False)
    FBS_campaign_id = serializers.CharField(max_length=8, min_length=8, required=False)
    DBS_campaign_id = serializers.CharField(max_length=8, min_length=8, required=False)
    business_id = serializers.CharField(max_length=8, min_length=8, required=False)

    class Meta:
        model = UserYaKeys
        fields = '__all__'

    def validate(self, data):
        """Проверяет юзера - собственника и привязку магазина"""
        user = self.context['request'].user
        method = self.context['request'].method
        existing_shop = UserYaKeys.objects.filter(user=user)

        if (method == 'POST') and existing_shop:
            raise serializers.ValidationError("Можно привязать не более 1-го магазина")
        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().update(instance, validated_data)


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор на планы подписок"""
    title = serializers.CharField(max_length=150)
    price = serializers.IntegerField()
    days_amount = serializers.IntegerField(max_value=365, min_value=3)

    class Meta:
        model = Subscription
        fields = ('id', 'title', 'price', 'days_amount')


class SubscriptedUserSerializer(serializers.ModelSerializer):
    expire_date = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptedUser
        fields = ('id', 'subscription_plan', 'user', 'start_date', 'expire_date')

    def get_expire_date(self, obj):
        start_date = obj.start_date
        expire_date = start_date + timedelta(days=30)
        return expire_date

    def create(self, validated_data):
        start_date = datetime.datetime.now()
        expire_date = start_date + timedelta(days=30)

        validated_data['expire_date'] = expire_date
        return super().create(validated_data)
