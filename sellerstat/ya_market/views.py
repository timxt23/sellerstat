import traceback

from django.db import transaction
from django.db.models import Prefetch
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Goods, PricesFBY, StocksFBY, UserCostPrice, UserDeliveredOrders
from .serializers import GoodsSerializer, PricesFBYSerializer, FBYStocksSerializer, UserCostPriceSerializer, \
    UserDeliveredOrdersSerializer, OrdersDateSerializer
from users.models import UserYaKeys
from .utils.request_goods import request_json_goods
from .utils.request_prices import request_json_prices
from users.permissions import IsUser
from .utils.request_stocks import request_json_stocks
from .utils.request_orders_delivered import request_json_delivered


class AddGoodsViewSet(viewsets.ModelViewSet):
    serializer_class = GoodsSerializer
    permission_classes = [IsAuthenticated, IsUser]

    def get_queryset(self):
        user = self.request.user
        if self.request.user.is_staff:
            return Goods.objects.all()
        return Goods.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        user_id = request.user.id
        user = User.objects.get(id=user_id)

        try:
            ya_api_keys = UserYaKeys.objects.get(user=request.user)
            oauth_key = ya_api_keys.ya_oauth_token
            bussines_id = ya_api_keys.business_id
            result = request_json_goods(oauth_key, bussines_id)
            goods_to_add = []
            for data in result:
                goods_instance = {
                    'user': user,
                    'sku': data.get('sku'),
                    'title': data.get('title'),
                    'category': data.get('category'),
                    'vendor': data.get('vendor'),
                    'barcode': data.get('barcode'),
                }
                goods_to_add.append(goods_instance)

            for good_data in goods_to_add:
                Goods.objects.update_or_create(
                    user=good_data['user'],
                    sku=good_data['sku'],
                    defaults=good_data
                )
            return Response({'result': result})
        except Exception as e:
            print(e)
            traceback.print_exc()
            return Response({'error': 'Error run add_goods'})


class GetPricesFBYViewSet(viewsets.ModelViewSet):
    serializer_class = PricesFBYSerializer
    permission_classes = [IsAuthenticated, IsUser]

    def get_queryset(self):
        user = self.request.user
        if self.request.user.is_staff:
            return PricesFBY.objects.all().prefetch_related(
                Prefetch('good_id', queryset=Goods.objects.only('sku', 'title'))
            )
        return PricesFBY.objects.filter(user=user).prefetch_related(
            Prefetch('good_id', queryset=Goods.objects.only('sku', 'title'))
        )

    def create(self, request, *args, **kwargs):
        user_id = request.user.id
        user = User.objects.get(id=user_id)

        try:
            ya_api_keys = UserYaKeys.objects.get(user=request.user)
            oauth = ya_api_keys.ya_oauth_token
            campaign_id = ya_api_keys.FBY_campaign_id
            request_skus = Goods.objects.filter(user=user_id)
            sku_list = list(request_skus.values_list('sku', flat=True))
            result = request_json_prices(oauth=oauth, campaign_id=campaign_id, skus=sku_list)
            price_to_create = []

            for data in result:
                checking_id = get_object_or_404(Goods, sku=data.get('sku'))
                sku = checking_id.sku
                if not 'value' in data:
                    continue
                if not sku == data.get('sku'):
                    print('Error check sku')
                    break
                prices_instance = {
                    'user': user,
                    'good_id': checking_id,
                    'price_value': data.get('value'),
                    'price_base': data.get('discountBase'),
                    'updated': data.get('updatedAt'),
                }
                price_to_create.append(prices_instance)

            for price_data in price_to_create:
                PricesFBY.objects.update_or_create(
                    user=price_data['user'],
                    good_id=price_data['good_id'],
                    defaults=price_data
                )

            return Response({'result': result})
        except Exception as e:
            print(e)
            return Response({'error': 'Error run GetPricesFBYViewSet'})


class GetStocksFBYViewSet(viewsets.ModelViewSet):
    serializer_class = FBYStocksSerializer
    permission_classes = [IsAuthenticated, IsUser]

    def get_queryset(self):
        user = self.request.user
        if self.request.user.is_staff:
            return StocksFBY.objects.all().prefetch_related(
                Prefetch('good_id', queryset=Goods.objects.only('sku', 'title'))
            )
        return StocksFBY.objects.filter(user=user).prefetch_related(
            Prefetch('good_id', queryset=Goods.objects.only('sku', 'title'))
        )

    def create(self, request, *args, **kwargs):
        user_id = request.user.id
        user = User.objects.get(id=user_id)

        try:
            ya_api_keys = UserYaKeys.objects.get(user=request.user)
            oauth = ya_api_keys.ya_oauth_token
            campaign_id = ya_api_keys.FBY_campaign_id

            request_skus = Goods.objects.filter(user=user_id).select_related('user')
            sku_to_id_mapping = {sku: id for sku, id in request_skus.values_list('sku', 'id')}
            result = request_json_stocks(
                oauth=oauth,
                campaign_id=campaign_id,
                skus=list(sku_to_id_mapping.keys())
            )
            stocks_to_create = []
            for data in result:
                checking_id = get_object_or_404(Goods, sku=data.get('shopSku'))
                sku = data.get('shopSku')
                if sku in sku_to_id_mapping:
                    stock_data = {
                        'user': user,
                        'good_id': checking_id,
                        'all_good_stocks': data.get('all_good_stocks'),
                        'agency_commission': data.get('agency_commission'),
                        'fee': data.get('fee'),
                        'fulfillment': data.get('fulfillment'),
                        'storage': data.get('storage'),
                        'withdraw': data.get('withdraw'),
                        'surplus': data.get('surplus')
                    }

                    stocks_to_create.append(stock_data)

                for stocks_data in stocks_to_create:
                    StocksFBY.objects.update_or_create(
                        user=stocks_data['user'],
                        good_id=stocks_data['good_id'],
                        defaults=stocks_data
                    )

            return Response({'result': result})
        except UserYaKeys.DoesNotExist:
            return Response({'error': 'UserYaKeys not found'})
        except Exception as e:
            print(e)
            return Response({'error': 'Error run GetStocksFBYViewSet'})


class UserCostsViewSet(viewsets.ModelViewSet):
    serializer_class = UserCostPriceSerializer
    permission_classes = [IsAuthenticated, IsUser]

    def get_queryset(self):
        user = self.request.user
        if self.request.user.is_staff:
            return UserCostPrice.objects.all().prefetch_related(
                Prefetch('good_id', queryset=Goods.objects.only('sku', 'title')),
                Prefetch('buy_currency'),
                Prefetch('delivery_currency')
            )
        return UserCostPrice.objects.filter(user=user).prefetch_related(
            Prefetch('good_id', queryset=Goods.objects.only('sku', 'title')),
            Prefetch('buy_currency'),
            Prefetch('delivery_currency')
        )


class UserDeliveredOrdersViewSet(viewsets.ModelViewSet):
    serializer_class = OrdersDateSerializer
    permission_classes = [IsAuthenticated, IsUser]

    def get_queryset(self):
        user = self.request.user
        if self.request.user.is_staff:
            return UserDeliveredOrders.objects.all().prefetch_related(
                Prefetch('good_id', queryset=Goods.objects.only('sku', 'title')),
            )
        return UserDeliveredOrders.objects.filter(user=user).prefetch_related(
            Prefetch('good_id', queryset=Goods.objects.only('sku', 'title')),
        )

    def create(self, request, *args, **kwargs):
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            try:
                date_from = serializer.validated_data.get('date_from').strftime('%Y-%m-%d')
                date_to = serializer.validated_data.get('date_to').strftime('%Y-%m-%d')
                ya_api_keys = UserYaKeys.objects.get(user=request.user)
                oauth = ya_api_keys.ya_oauth_token
                campaign_id = ya_api_keys.FBY_campaign_id

                result = request_json_delivered(
                    oauth=oauth,
                    campaign_id=campaign_id,
                    date_from=date_from,
                    date_to=date_to
                )

                orders_to_create = []

                goods = Goods.objects.all()
                good_dict = {good.sku: good for good in goods}
                for data in result:
                    # checking_id = get_object_or_404(Goods, sku=data.get('good_sku'))
                    order = UserDeliveredOrders(
                        user=user,
                        good_id=good_dict.get(data.get('good_sku')),
                        order_id=data.get('order_id'),
                        creation_date=data.get('creation_date'),
                        delivered_date=data.get('delivered_date'),
                        good_sku=data.get('good_sku'),
                        items_count=data.get('items_count'),
                        delivery_region=data.get('delivery_region'),
                        warehouse_name=data.get('warehouse_name'),
                        bid_fee=data.get('bid_fee'),
                        payment_total=data.get('payment_total'),
                        commission_delivery=data.get('commission_delivery'),
                        commission_fee=data.get('commission_fee'),
                        auction_total=data.get('auction_total'),
                    )
                    orders_to_create.append(order)

                fields = [
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
                ]
                with UserDeliveredOrders.objects.bulk_update_or_create_context(
                        fields,
                        match_field='order_id',
                        batch_size=50) as bulkit:
                    for i in orders_to_create:
                        bulkit.queue(i)

                return Response({'result': result})

            except UserYaKeys.DoesNotExist:
                return Response({'error': 'UserYaKeys not found'})
            except Exception as e:
                print(e)
                return Response({'error': f'Error run GetStocksFBYViewSet - {e}'})
