from datetime import timedelta

from django.db import transaction
from rest_framework import serializers

from .models import Goods, PricesFBY, StocksFBY, Currency, UserCostPrice, CurrencyList, UserDeliveredOrders


class GoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = '__all__'
        read_only_fields = ('id', 'sku')


class OrdersDateSerializer(serializers.Serializer):
    date_from = serializers.DateField()
    date_to = serializers.DateField()

    def validate_date_from(self, value):
        import re
        date_format = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(date_format, value.strftime('%Y-%m-%d')):
            raise serializers.ValidationError('Формат даты не YYYY-MM-DD')
        return value

    def validate_date_to(self, value):
        import re
        date_format = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(date_format, value.strftime('%Y-%m-%d')):
            raise serializers.ValidationError('Формат даты не YYYY-MM-DD')
        return value

    def validate(self, data):
        date_from = data.get('date_from')
        date_to = data.get('date_to')

        if date_from > date_to:
            raise serializers.ValidationError('Дата начала должна быть меньше или равна дате окончания')
        if (date_to - date_from) > timedelta(days=180):
            raise serializers.ValidationError('Период должен быть не более 180 дней')

        return data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['date_from'] = ret['date_from'].strftime('%Y-%m-%d')
        ret['date_to'] = ret['date_to'].strftime('%Y-%m-%d')
        return ret


class UserDeliveredOrdersSerializer(serializers.ModelSerializer):
    good_title = serializers.SerializerMethodField()

    class Meta:
        model = UserDeliveredOrders
        fields = (
            'order_id',
            'creation_date',
            'delivered_date',
            'good_title',
            'good_sku',
            'items_count',
            'delivery_region',
            'warehouse_name',
            'bid_fee',
            'payment_total',
            'commission_delivery',
            'commission_fee',
            'auction_total',
        )
    def get_good_title(self, obj):
        return obj.good_id.sku if obj.good_id else None


class PricesFBYSerializer(serializers.ModelSerializer):
    good_sku = serializers.SerializerMethodField()
    good_title = serializers.SerializerMethodField()

    class Meta:
        model = PricesFBY
        fields = ('good_id', 'good_sku', 'good_title', 'price_value', 'price_base', 'updated')
        read_only_fields = ('id', 'updated', 'good_id', 'user')

    def get_good_sku(self, obj):
        return obj.good_id.sku if obj.good_id else None

    def get_good_title(self, obj):
        return obj.good_id.title if obj.good_id else None


class FBYStocksSerializer(serializers.ModelSerializer):
    good_sku = serializers.SerializerMethodField()
    good_title = serializers.SerializerMethodField()

    class Meta:
        model = StocksFBY
        fields = (
            'good_sku',
            'good_title',
            'all_good_stocks',
            'agency_commission',
            'fee',
            'fulfillment',
            'storage',
            'withdraw',
            'surplus',
        )
        # read_only_fields = ('__all__',)

    def get_good_sku(self, obj):
        return obj.good_id.sku if obj.good_id else None

    def get_good_title(self, obj):
        return obj.good_id.title if obj.good_id else None


class UserCostPriceSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    good_sku = serializers.SerializerMethodField()
    buy_price = serializers.FloatField(required=True)
    buy_currency = serializers.SerializerMethodField()
    buy_currency_rate = serializers.FloatField(default=1)
    delivery_price = serializers.FloatField(default=0)
    delivery_currency = serializers.SerializerMethodField()
    delivery_currency_rate = serializers.FloatField(default=1)
    fulfilment_price = serializers.FloatField(default=0)

    class Meta:
        model = UserCostPrice
        fields = (
            'user',
            'good_sku',
            'buy_price',
            'buy_currency',
            'buy_currency_rate',
            'delivery_price',
            'delivery_currency',
            'delivery_currency_rate',
            'fulfilment_price'
        )

    def get_good_sku(self, obj):
        return obj.good_id.sku if obj.good_id else None

    def get_buy_currency(self, obj):
        return obj.buy_currency.code if obj.buy_currency else None

    def get_delivery_currency(self, obj):
        return obj.delivery_currency.code if obj.delivery_currency else None

    @transaction.atomic
    def create(self, validated_data):
        good_sku = self.context['view'].request.data['good_sku']
        buy_currency_context = self.context['view'].request.data['buy_currency']
        delivery_currency_context = self.context['view'].request.data['delivery_currency']
        user = self.context['request'].user

        try:
            good = Goods.objects.only('id', 'sku').get(sku=good_sku)
            buy_currency = CurrencyList.objects.get(code=buy_currency_context)
            delivery_currency = CurrencyList.objects.get(code=delivery_currency_context)
        except Goods.DoesNotExist:
            raise serializers.ValidationError(
                f'Товара с SKU {good_sku} не существут. Обновите товары!'
            )
        except CurrencyList.DoesNotExist:
            raise serializers.ValidationError(
                f'Валюты {buy_currency_context} не существует'
            )

        data = {
            "buy_price": validated_data['buy_price'],
            "buy_currency": buy_currency,
            "buy_currency_rate": validated_data['buy_currency_rate'],
            "delivery_price": validated_data['delivery_price'],
            "delivery_currency": delivery_currency,
            "delivery_currency_rate": validated_data['delivery_currency_rate'],
            "fulfilment_price": validated_data['fulfilment_price']
        }

        user_cost_price, created = UserCostPrice.objects.update_or_create(
            user=user,
            good_id=good,
            defaults=data
        )
        return user_cost_price
