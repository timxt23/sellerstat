from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import UserYaKeys, Subscription, SubscriptedUser
from .permissions import IsUser, IsAdmin, IsAdminOrReadOnly
from .serializers import UserYaKeysSerializer, SubscriptionSerializer, SubscriptedUserSerializer


class UserYaKeysViewSet(viewsets.ModelViewSet):
    serializer_class = UserYaKeysSerializer
    permission_classes = [IsAuthenticated, IsUser]
    http_method_names = ['get', 'patch', 'post']

    def get_queryset(self):
        user = self.request.user
        return UserYaKeys.objects.filter(user=user)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAdmin,)


class SubsrciptedUserViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptedUserSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if self.request.user.is_staff:
            return SubscriptedUser.objects.all()
        return SubscriptedUser.objects.filter(user=user)
