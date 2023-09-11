from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AddGoodsViewSet, GetPricesFBYViewSet, GetStocksFBYViewSet, UserCostsViewSet, \
    UserDeliveredOrdersViewSet

app_name = 'ya_market'

router = DefaultRouter()
router.register('add_goods', AddGoodsViewSet, basename='add_goods')
router.register('get_price', GetPricesFBYViewSet, basename='get_price')
router.register('get_stocks', GetStocksFBYViewSet, basename='get_stocks')
router.register('costs', UserCostsViewSet, basename='costs')
router.register('get_delivered', UserDeliveredOrdersViewSet, basename='get_delivered')


urlpatterns = [
    path('', include(router.urls)),
]