import json
import requests


def load_prices(json_response):
    # with open(path, 'r') as json_file:
    data = json_response
    sku_prices = []
    print('Начинаем парсинг')
    for offers in data['result']['offers']:
        for key, value in offers.items():
            response = {}
            if key == 'offerId':
                # print(f'{key} -- {value}')
                response = {f'sku': value}
                if 'campaignPrice' in offers:
                    response['value'] = offers['campaignPrice']['value']
                    response['discountBase'] = offers['campaignPrice']['discountBase']
                    response['updatedAt'] = offers['campaignPrice']['updatedAt']
                sku_prices.append(response)
            pass
    print('Парсинг закончен')
    return sku_prices


def request_json_prices(oauth, campaign_id, skus):
    path = f'https://api.partner.market.yandex.ru/campaigns/{campaign_id}/offers'
    headers = {
        "Authorization": f"Bearer {str(oauth)}",
        "Content-Type": "application/json",
        "User-Agent": "PostmanRuntime/7.32.3"
    }
    data = {"offerIds": skus}
    response = requests.post(path, data=json.dumps(data), headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(response.status_code)
        # sku = load_sku(result)
        return load_prices(json_response=result)
    else:
        print(response.status_code, response.text)

