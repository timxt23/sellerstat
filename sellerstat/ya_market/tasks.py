from celery import shared_task

from .utils.update_currency import update_currency_today_fr_xml_cbr


@shared_task
def upadte_currency_task():
    update_currency_today_fr_xml_cbr()