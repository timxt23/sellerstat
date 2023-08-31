from django_cron import CronJobBase, Schedule

from ..utils.update_currency import update_currency_today_fr_xml_cbr


class UpdateCurrencyRates(CronJobBase):
    RUN_AT_TIMES = ['13:00']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'ya_market.update_currency'

    def do(self):
        update_currency_today_fr_xml_cbr()