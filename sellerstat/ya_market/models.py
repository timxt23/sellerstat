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
        return f'SKU - {self.sku} - {self.title} пользователя {self.user}'


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
        Currency,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Валюта Закупа',
        related_name='buy_currency'
    )
    buy_currency_rate = models.FloatField(
        max_length=5,
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
        Currency,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Валюта доставки',
        related_name='delivery_currency'
    )
    delivery_currency_rate = models.FloatField(
        max_length=5,
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
