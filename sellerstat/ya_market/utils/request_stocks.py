import json

import requests


"""def load_stocks(json_response, skus):
    # with open(path, 'r') as json_file:
    data = json_response
    sku_stocks = []
    print('Начинаем парсинг')
    for offers in data['result']['shopSkus']:
        for key, value in offers.items():
            response = {}
            if (key == 'shopSku') and (value in skus):
                # print(f'{key} -- {value}')
                response = {f'shopSku': value}
                if 'warehouses' in offers:
                    response['all_good_stocks'] = warehouse_parse(offers['warehouses'])
                if 'tariffs' in offers:
                    tariffs = tariffs_parse(offers['tariffs'])
                    for tariff_type, amount in tariffs.items():
                        response[tariff_type] = amount
                sku_stocks.append(response)
            pass
    print('Парсинг закончен')
    return sku_stocks"""
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


"""def tariffs_parse(tarifs):
    tariffs_dict = {}
    for tariff in tarifs:
        amount = tariff['amount']
        for key, value in tariff.items():
            if key == 'type':
                tariffs_dict[value.lower()] = amount
            pass
    return tariffs_dict"""
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

oauth = 'y0_AgAAAABj2d1NAAowIQAAAADn1jWaqJR95xZAQJWVU163GwYwcJVT_N0'
campid = '58157088'
skus = ["ZH-003", "TL-002"]
print(request_json_stocks(oauth, campid, skus))