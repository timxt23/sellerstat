from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AddGoodsViewSet, GetPricesFBYViewSet, GetStocksFBYViewSet

app_name = 'ya_market'

router = DefaultRouter()
router.register('add_goods', AddGoodsViewSet, basename='add_goods')
router.register('get_price', GetPricesFBYViewSet, basename='get_price')
router.register('get_stocks', GetStocksFBYViewSet, basename='get_stocks')

urlpatterns = [
    path('', include(router.urls)),
]