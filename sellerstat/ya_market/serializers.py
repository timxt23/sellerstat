from rest_framework import serializers

from .models import Goods, PricesFBY, StocksFBY, Currency, UserCostPrice


class GoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = '__all__'
        read_only_fields = ('id', 'sku')

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
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())  # Скрываем поле и назначаем тек. юзера
    good_id = serializers.CharField(source='goods.sku', required=True)
    buy_price = serializers.FloatField(required=True)
    buy_currency = serializers.CharField(source='currency.code', required=True)
    delivery_price = serializers.FloatField(required=True)
    delivery_currency = serializers.CharField(source='currency.code')
    fulfilment_price = serializers.FloatField(required=True)

    class Meta:
        model = UserCostPrice
        field = (
            'good_id',
            'buy_price',
            'buy_currency',
            'delivery_price',
            'delivery_currency',
            'fulfilment_price'
        )
