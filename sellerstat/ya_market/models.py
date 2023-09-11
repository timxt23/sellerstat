from bulk_update_or_create import BulkUpdateOrCreateQuerySet
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Goods(models.Model):
    """Модель Товаров которые принадлежат пользователю"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Товар пользователя'
    )
    sku = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='SKU',
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Название товара'
    )
    category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Категория товара'
    )
    vendor = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Бренд'
    )
    barcode = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Первый баркод'
    )

    class Meta:
        verbose_name = 'Товар пользователя'
        verbose_name_plural = 'Товары пользователей'
        ordering = ['sku']
        constraints = [
            models.UniqueConstraint(fields=['sku'], name='unique sku')
        ]

    def __str__(self):
        return f'{self.sku} - {self.title}'


class PricesFBY(models.Model):
    """Модель цена которые относятся к товарам и пользователям"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Товар пользователя'
    )
    good_id = models.ForeignKey(
        Goods,
        on_delete=models.CASCADE,
        verbose_name='Товар',
        related_name='price_fby'
    )
    price_value = models.PositiveIntegerField(
        max_length=6,
        verbose_name='Цена'
    )
    price_base = models.PositiveIntegerField(
        max_length=6,
        verbose_name='Цена до скидки'
    )
    updated = models.DateTimeField()

    class Meta:
        verbose_name = 'Цена товара'
        verbose_name_plural = 'Цены товаров'
        constraints = [
            models.UniqueConstraint(fields=['good_id'], name='unique goods')
        ]

    def __str__(self):
        return f'SKU - {self.good_id} цена {self.price_value}. Цена до скидки {self.price_base}'


class StocksFBY(models.Model):
    """Модель остатков и тарифов МП каждого товара"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Остатки пользователя',
    )
    good_id = models.ForeignKey(
        Goods,
        on_delete=models.CASCADE,
        verbose_name='Товар',
        related_name='stock_fby'
    )
    all_good_stocks = models.PositiveIntegerField(
        max_length=5,
        null=True,
        blank=True,
        verbose_name='Остатки для продажи'
    )
    agency_commission = models.FloatField(
        max_length=8,
        null=True,
        blank=True,
        default=0.0,
        verbose_name='Обработка платежа',
        help_text='Прием и перечисление денег от покупателя (агентское вознаграждение)'
    )
    fee = models.FloatField(
        max_length=8,
        null=True,
        blank=True,
        default=0.0,
        verbose_name='Стоимость размещения',
        help_text='Размещение товара на Маркете'
    )
    fulfillment = models.FloatField(
        max_length=8,
        null=True,
        blank=True,
        default=0.0,
        verbose_name='Обработка на складе',
        help_text='Обработка товара на складе Маркета'
    )
    storage = models.FloatField(
        max_length=8,
        null=True,
        blank=True,
        default=0.0,
        verbose_name='Стоимость хранения',
        help_text='Хранение товара на складе Маркета в течение суток'
    )
    withdraw = models.FloatField(
        max_length=8,
        null=True,
        blank=True,
        default=0.0,
        verbose_name='Возврат со склада',
        help_text='Вывоз товара со склада Маркета'
    )
    surplus = models.FloatField(
        max_length=8,
        null=True,
        blank=True,
        default=0.0,
        verbose_name='Хранение излишков',
        help_text='Хранение излишков на складе Маркета'
    )

    class Meta:
        verbose_name = 'Остаток товара и тарифы'
        verbose_name_plural = 'Остатки товара и тарифы'
        constraints = [
            models.UniqueConstraint(fields=['good_id'], name='unique goods in stocks')
        ]

    def __str__(self):
        return f'SKU - {self.good_id}, Остаток - {self.all_good_stocks}.'


class CurrencyList(models.Model):
    '''Модель списка курсов для себестоимости'''
    code = models.CharField(
        max_length=3,
        verbose_name='Валюта'
    )
    class Meta:
        verbose_name = 'Валюта'
        verbose_name_plural = 'Валюты'
        constraints = [
            models.UniqueConstraint(fields=['code'], name='unique code currency_list')
        ]

    def __str__(self):
        return f'{self.code}'


class Currency(models.Model):
    '''Модель курсов валют к рублю'''
    code = models.CharField(
        max_length=3,
        verbose_name='Валюта'
    )
    date = models.DateTimeField(
        verbose_name='Дата курса'
    )
    value = models.FloatField(
        max_length=5,
        verbose_name='Курс'
    )

    class Meta:
        verbose_name = 'Курс валюты'
        verbose_name_plural = 'Курсы валют'

    def __str__(self):
        return f'Валюта - {self.code}, Курс - {self.value} от {self.date}.'


class UserCostPrice(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Себестоимость пользователя',
    )
    good_id = models.ForeignKey(
        Goods,
        on_delete=models.CASCADE,
        verbose_name='Товара',
        related_name='costs_fby'
    )
    buy_price = models.FloatField(
        max_length=6,
        verbose_name='Цена 1 шт',
        help_text='Себестоимость 1 шт (без доставки)'
    )
    buy_currency = models.ForeignKey(
        CurrencyList,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Валюта Закупа',
        related_name='buy_currency'
    )
    buy_currency_rate = models.FloatField(
        max_length=5,
        blank=True,
        null=True,
        verbose_name='Курс покупки',
        help_text='Курс по которому купили'
    )
    delivery_price = models.FloatField(
        max_length=6,
        blank=True,
        null=True,
        verbose_name='Доставка 1 шт',
        help_text='Стоимость доставки 1 шт'
    )
    delivery_currency = models.ForeignKey(
        CurrencyList,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Валюта доставки',
        related_name='delivery_currency'
    )
    delivery_currency_rate = models.FloatField(
        max_length=5,
        blank=True,
        null=True,
        verbose_name='Курс доставки',
        help_text='Курс по которому доставили'
    )
    fulfilment_price = models.FloatField(
        max_length=5,
        blank=True,
        null=True,
        verbose_name='Складская обработка',
        help_text='Стоимость складской обработки у продавца 1 шт'
    )

    class Meta:
        verbose_name = 'Себестоимость товара'
        verbose_name_plural = 'Себестоимости товаров'

    def __str__(self):
        return f'Себестоимость товара {self.good_id}'


class UserDeliveredOrders(models.Model):
    """Модель доставленных заказов продавца (юзера)"""
    objects = BulkUpdateOrCreateQuerySet.as_manager()

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Продажи Пользователя',
        related_name='delivered_orders'
    )
    good_id = models.ForeignKey(
        Goods,
        on_delete=models.CASCADE,
        verbose_name='Продажа товара',
        related_name='delivered_good'
    )
    order_id = models.CharField(
        max_length=10,
        verbose_name='Номер заказа',
    )
    creation_date = models.DateField(
        verbose_name='Дата заказа'
    )
    delivered_date = models.DateTimeField(
        verbose_name='Дата доставки'
    )
    good_sku = models.CharField(
        max_length=20,
        verbose_name='SKU товара'
    )
    items_count = models.IntegerField(
        verbose_name='Количество'
    )
    delivery_region = models.CharField(
        max_length=50,
        verbose_name='Регион доставки',
        default='Нет указан'
    )
    warehouse_name = models.CharField(
        max_length=30,
        verbose_name='Склад',
        default='Нет указан'
    )
    bid_fee = models.FloatField(
        verbose_name='Процент Буста',
        null=True,
        default=0
    )
    payment_total = models.FloatField(
        verbose_name='Сумма заказа'
    )
    commission_delivery = models.FloatField(
        verbose_name='Доставка',
        help_text='Стоимость доставки',
        default=0
    )
    commission_fee = models.FloatField(
        verbose_name='Комисся',
        help_text='Все комиссии кроме доставки и рекламы',
        default=0
    )
    auction_total = models.FloatField(
        verbose_name='Буст',
        help_text='Стоимость буста продаж',
        default=0,
        null=True
    )

    class Meta:
        verbose_name = 'Список заказов'
        verbose_name_plural = 'Списки заказов'
        constraints = [
            models.UniqueConstraint(fields=['order_id'], name='unique order_id')
        ]
        ordering = ['-creation_date']

    def __str__(self):
        return f'{self.order_id} от {self.creation_date}.'
