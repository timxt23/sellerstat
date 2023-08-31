from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('users.urls', namespace='users')),
    path('api/v1/', include('ya_market.urls', namespace='ya_market')),
    # path('api/v1/', include('ya_market.urls', namespace='ya_market')),
]
