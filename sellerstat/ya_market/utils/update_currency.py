import requests
import xml.etree.ElementTree as ET
from datetime import date, datetime

from ..models import Currency
from sellerstat.settings import CURRENCIES_CBR


def update_currency_today_fr_xml_cbr():
    today = date.today().strftime('%d/%m/%Y')
    response = requests.get(f'https://www.cbr.ru/scripts/XML_daily.asp?date_req={today}')
    xml_content = response.content

    root = ET.fromstring(xml_content)
    for valute in root.findall('Valute'):
        if valute.get('ID') in CURRENCIES_CBR.values():
            date_rate = str(datetime.today())
            code = valute.find('CharCode').text
            value = round(float(valute.find('Value').text.replace(',', '.')), 2)
            print(value)
            Currency.objects.update_or_create(
                code=code,
                date=date_rate,
                defaults={'value': value},
            )

    return True
