from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserYaKeysViewSet, SubscriptionViewSet, SubsrciptedUserViewSet

app_name = 'users'

router = DefaultRouter()
router.register('ya_api_keys', UserYaKeysViewSet, basename='ya_api_keys')
router.register('plans', SubscriptionViewSet, basename='plans')
router.register('user_plans', SubsrciptedUserViewSet, basename='user_plans')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]