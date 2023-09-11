import json

import requests


def load_stocks(json_response, skus):
    sku_stocks = []
    shop_skus = json_response['result']['shopSkus']

    print('Начинаем парсинг')
    for offers in shop_skus:
        shop_sku = offers.get('shopSku')
        if shop_sku in skus:
            response = {'shopSku': shop_sku}

            warehouses = offers.get('warehouses')
            if warehouses:
                response['all_good_stocks'] = warehouse_parse(warehouses)

            tariffs = offers.get('tariffs')
            if tariffs:
                tariff_data = tariffs_parse(tariffs)
                response.update(tariff_data)

            sku_stocks.append(response)

    print('Парсинг закончен')
    return sku_stocks


def tariffs_parse(tarifs):
    return {
        tariff['type'].lower(): tariff['amount'] for tariff in tarifs
    }


def warehouse_parse(warehouses):
    sum_stocks = 0
    for warehouse in warehouses:
        for key in warehouse['stocks']:
            if key['type'] == ('FIT' or 'AVAILABLE'):
                sum_stocks += int(key['count'])
    return sum_stocks


def request_json_stocks(oauth, campaign_id, skus):
    path = f'https://api.partner.market.yandex.ru/campaigns/{campaign_id}/stats/skus'
    headers = {
        "Authorization": f"Bearer {str(oauth)}",
        "Content-Type": "application/json",
        "User-Agent": "PostmanRuntime/7.32.3"
    }
    data = {"shopSkus": skus}
    response = requests.post(path, data=json.dumps(data), headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(response.status_code)
        return load_stocks(json_response=result, skus=skus)
    else:
        print(response.status_code, response.text)
