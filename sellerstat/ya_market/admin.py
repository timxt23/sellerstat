from django.contrib import admin

from .models import Goods, PricesFBY, StocksFBY, Currency, UserCostPrice, CurrencyList, UserDeliveredOrders


class GoodsAdmin(admin.ModelAdmin):
    list_display = ('sku', 'title', 'vendor', 'category', 'barcode')


class PriceFBYAdmin(admin.ModelAdmin):
    list_display = ('good_id', 'price_value', 'price_base')


class StocksFBYAdmin(admin.ModelAdmin):
    list_display = (
        'good_id',
        'all_good_stocks',
        'agency_commission',
        'fee',
        'fulfillment',
        'storage',
        'withdraw'
    )


class UserCostPriceAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'good_id',
        'buy_price',
        'buy_currency',
        'buy_currency_rate',
        'delivery_price',
        'delivery_currency',
        'delivery_currency_rate',
        'fulfilment_price'
    )


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'value', 'date')


class CurrencyListAdmin(admin.ModelAdmin):
    list_display = ('code',)


class UserDeliveredOrdersAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'order_id',
        'creation_date',
        'delivered_date',
        'good_sku',
        'items_count',
        'delivery_region',
        'warehouse_name',
        'bid_fee',
        'payment_total',
        'commission_delivery',
        'commission_fee',
        'auction_total'
    )


admin.site.register(Goods, GoodsAdmin)
admin.site.register(PricesFBY, PriceFBYAdmin)
admin.site.register(StocksFBY, StocksFBYAdmin)
admin.site.register(UserCostPrice, UserCostPriceAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(CurrencyList, CurrencyListAdmin)
admin.site.register(UserDeliveredOrders, UserDeliveredOrdersAdmin)
