from django.contrib import admin

from .models import Subscription, SubscriptedUser


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'days_amount')


class SubscriptedUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_plan', 'start_date', 'expire_date')


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(SubscriptedUser, SubscriptedUserAdmin)
