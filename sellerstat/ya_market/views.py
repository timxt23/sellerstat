import traceback

from django.db.models import Prefetch
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Goods, PricesFBY, StocksFBY
from .serializers import GoodsSerializer, PricesFBYSerializer, FBYStocksSerializer
from users.models import UserYaKeys
from .utils.request_goods import request_json_goods
from .utils.request_prices import request_json_prices
from users.permissions import IsUser
from .utils.request_stocks import request_json_stocks


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
            id_list = list(request_skus.values_list('id', flat=True))
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