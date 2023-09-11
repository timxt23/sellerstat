import json
import requests


def load_stocks(json_response):
    orders_to_create = []
    orders = json_response['result']['orders']

    for order in orders:
        bid_fee = order['items'][0].get('bidFee')
        bid_fee_value = 0 if bid_fee is None else bid_fee / 100
        response = {
            'order_id': order.get('id'),
            'creation_date': order.get('creationDate'),
            'delivered_date': order.get('statusUpdateDate'),
            'good_sku': order['items'][0].get('shopSku'),
            'delivery_region': order['deliveryRegion'].get('name'),
            'warehouse_name': order['items'][0]['warehouse'].get('name'),
            'bid_fee': bid_fee_value,
            'payment_total': parse_payment_total(order['payments']),
            'commission_delivery': parse_commission_delivery(order['commissions']),
            'commission_fee': parse_commission_fee_all(order['commissions']),
            'auction_total': parse_auction_total(order['commissions']),
            'items_count': order['items'][0].get('count'),
        }

        # проверяем нет ли дубликатов в списке orders_to_create
        if not any(o['order_id'] == response['order_id'] for o in orders_to_create):
            orders_to_create.append(response)

    return orders_to_create


def parse_auction_total(delivery_fees):
    type_needed = 'AUCTION_PROMOTION'
    return next((fee['actual'] for fee in delivery_fees if fee['type'] == type_needed), None)


def parse_commission_fee_all(all_fee):
    types_needed = [
        'FEE',
        'FULFILLMENT',
        'PAYMENT_TRANSFER',
        'AGENCY',
        'LOYALTY_PARTICIPATION_FEE'
    ]
    return round(sum(fee['actual'] for fee in all_fee if fee['type'] not in ('DELIVERY_TO_CUSTOMER',
                                                                             'AUCTION_PROMOTION')), 2)


def parse_commission_delivery(delivery_fees):
    type_needed = 'DELIVERY_TO_CUSTOMER'
    delivery = next((fee['actual'] for fee in delivery_fees if fee['type'] == type_needed), None)
    delivery_fee = 0 if delivery is None else delivery
    return delivery_fee


def parse_payment_total(payments):
    return sum(payment['total'] for payment in payments)


def request_json_delivered(oauth, campaign_id, date_from, date_to, page=None):
    path = f'https://api.partner.market.yandex.ru/campaigns/{campaign_id}/stats/orders/'
    headers = {
        "Authorization": f"Bearer {str(oauth)}",
        "Content-Type": "application/json",
        "User-Agent": "PostmanRuntime/7.32.3"
    }
    query_params = {
        "page_token": page,
        "limit": 200
    }
    data = {
        "statuses": ["DELIVERED"],
        "dateFrom": date_from,
        "dateTo": date_to,
    }
    response = requests.post(
        path,
        data=json.dumps(data),
        headers=headers,
        params=query_params
    )
    if response.status_code == 200:
        result = response.json()
        orders = load_stocks(json_response=result)
        page_token = result['result']['paging']
        if 'nextPageToken' in page_token:
            next_page = request_json_delivered(
                oauth,
                campaign_id,
                date_from, date_to,
                page_token['nextPageToken'])

            orders.extend(next_page)
        print(response.status_code)
        return orders
    else:
        print(response.status_code, response.text)
