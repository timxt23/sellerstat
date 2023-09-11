from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Subscription(models.Model):
    """Модель плана платной подписки пользователя"""
    title = models.CharField(
        max_length=150,
        verbose_name='Название'
    )
    price = models.IntegerField(
        max_length=10,
        verbose_name='Цена',
    )
    days_amount = models.PositiveIntegerField(
        max_length=4,
        verbose_name='Кол-во дней',
    )

    class Meta:
        verbose_name = 'План подписки'
        verbose_name_plural = 'Планы подписки'
        ordering = ['title']

    def __str__(self) -> str:
        return f'План {self.title} на {self.days_amount} за {self.price}р.'


class SubscriptedUser(models.Model):
    """Модель подписки юзера на план"""
    subscription_plan = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        verbose_name='План подписки',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик на план'
    )
    start_date = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата старта плана',
    )
    expire_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата окончания плана',
    )

    class Meta:
        verbose_name = 'План подписки пользователя'
        verbose_name_plural = 'Планы подписки пользователей'
        ordering = ['-start_date']

    def __str__(self) -> str:
        return (f'Подписка - {self.subscription_plan} пользователя {self.user} '
                f'с {self.start_date} до {self.expire_date}.')


class UserYaKeys(models.Model):
    """Модель хранения api-ключей пользователей"""
    user = models.ForeignKey(
        User,
        related_name='ya_api_keys',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    FBY_campaign_id = models.BigIntegerField(
        max_length=8,
        null=True,
        blank=True,
        verbose_name='Id FBY кампании Yandex',
    )
    FBS_campaign_id = models.BigIntegerField(
        max_length=8,
        null=True,
        blank=True,
        verbose_name='Id FBS кампании Yandex',
    )
    DBS_campaign_id = models.BigIntegerField(
        max_length=8,
        null=True,
        blank=True,
        verbose_name='Id DBS кампании Yandex',
    )
    ya_oauth_token = models.CharField(
        max_length=100,
        verbose_name='OAuth токен Яндекса'
    )
    business_id = models.CharField(
        max_length=8,
        verbose_name='BusinessId кабинета',
        blank=True
    )

    class Meta:
        verbose_name = 'Яндекс ключи пользователя'
        verbose_name_plural = 'Яндекс ключи пользователей'
        ordering = ['user']
        constraints = [
            models.UniqueConstraint(fields=['ya_oauth_token'], name='unique oauth')
        ]

    def __str__(self) -> str:
        return (f'Ключи пользователя {self.user} - FBY:{self.FBY_campaign_id};'
                f'FBS:{self.FBS_campaign_id}; DBS:{self.DBS_campaign_id};'
                f'OAuth:{self.ya_oauth_token};')
