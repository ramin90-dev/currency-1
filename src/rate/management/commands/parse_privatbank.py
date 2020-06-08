from datetime import date, timedelta

from django.core.management.base import BaseCommand

import rate.model_choices as mch
from rate.models import Rate
from rate.utils import to_decimal

import requests


def date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


class Command(BaseCommand):
    help = 'Parse rates from 2016 PrivatBank'  # noqa  django requires 'help'

    def handle(self, *args, **options):
        start_date = date(2016, 12, 1)
        end_date = date.today()

        currency_type_mapper = {
            'USD': mch.SOURCE_TYPE_USD,
            'EUR': mch.SOURCE_TYPE_EUR,
        }

        for single_date in date_range(start_date, end_date):
            url = f'https://api.privatbank.ua/p24api/exchange_rates?json&date={single_date.strftime("%d.%m.%Y")}'
            response = requests.get(url).json()
            for item in response['exchangeRate']:
                if 'currency' not in item or item['currency'] not in currency_type_mapper:
                    continue

                currency_type = currency_type_mapper[item['currency']]

                # buy
                amount = to_decimal(item['purchaseRate']) if 'purchaseRate' in item else to_decimal(
                    item['purchaseRateNB'])

                Rate.objects.create(amount=amount,
                                    source=mch.SOURCE_PRIVATBANK,
                                    currency_type=currency_type,
                                    type=mch.RATE_TYPE_BUY,
                                    )

                last = Rate.objects.filter(source=mch.SOURCE_PRIVATBANK,
                                           currency_type=currency_type,
                                           type=mch.RATE_TYPE_BUY,
                                           ).last()

                last.created = single_date
                last.save()

                # sale
                amount = to_decimal(item['saleRate']) if 'saleRate' in item else to_decimal(item['saleRateNB'])

                Rate.objects.create(amount=amount,
                                    source=mch.SOURCE_PRIVATBANK,
                                    currency_type=currency_type,
                                    type=mch.RATE_TYPE_SALE,
                                    )

                last = Rate.objects.filter(source=mch.SOURCE_PRIVATBANK,
                                           currency_type=currency_type,
                                           type=mch.RATE_TYPE_SALE,
                                           ).last()

                last.created = single_date
                last.save()
