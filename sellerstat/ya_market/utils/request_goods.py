import json
import requests


def load_sku(json_response):
    # with open(path, 'r') as json_file:
    data = json_response
    skus = []
    print('Начинаем парсинг')
    for items in data['result']['offerMappings']:
        for offers in items.values():
            for key, value in offers.items():
                response = {}
                if key == 'offerId':
                    # print(f'{key} -- {value}')
                    response = {f'sku': value}
                    if 'name' in offers:
                        response['title'] = offers['name']
                    if 'category' in offers:
                        response['category'] = offers['category']
                    if 'vendor' in offers:
                        response['vendor'] = offers['vendor']
                    if 'barcodes' in offers:
                        response['barcode'] = offers['barcodes'][0]
                    skus.append(response)
                pass
    print('Парсинг закончен')
    return skus


def request_json_goods(oauth, business_id):
    path = f'https://api.partner.market.yandex.ru/businesses/{business_id}/offer-mappings?page_token=&limit='
    headers = {
        "Authorization": f"Bearer {str(oauth)}",
        "Content-Type": "application/json",
        "User-Agent": "PostmanRuntime/7.32.3"
    }
    data = {}
    response = requests.post(path, data=json.dumps(data), headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(response.status_code)
        # sku = load_sku(result)
        return load_sku(json_response=result)
    else:
        print(response.status_code, response.text)
