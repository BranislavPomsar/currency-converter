import argparse
import json

from requests_html import HTMLSession
from redis import StrictRedis
from datetime import datetime


def get_rates():

    rates = None

    rates_key = f'rates_{datetime.now().date()}'

    data = load_from_redis(rates_key)

    if not data:

        try:

            session = HTMLSession()
            r = session.get("https://api.exchangeratesapi.io/latest")
            data = r.json()

        except Exception:

            print('Error getting exchange list')

        if data:

            save_to_redis(rates_key, data)

    if data:

        rates = data.get("rates")
        rates.update({"EUR": 1})

    return rates


def convert(currency_from, currency_to, amount):

    rates = get_rates()

    if rates:

        currency_from = symbol_to_currency(currency_from)
        currency_to = symbol_to_currency(currency_to)

        rate_from = rates.get(currency_from)

        if not rate_from:

            print("Invalid input currency")
            return None

        if rate_from:

            out = {'input': {'amount': amount, 'currency': currency_from},
                   'output': {}}

            if currency_to:

                rate_to = rates.get(currency_to)

                if not rate_to:

                    print("Invalid output currency")
                    return None

                out.get('output').update({currency_to: calc(rate_to, rate_from, amount)})

            else:

                for key, value in rates.items():
                    out.get('output').update({key: calc(value, rate_from, amount)})

            return json.dumps(out)

    return None


def calc(rate_from: float, rate_to: float, amount: float):

    return round(rate_from / rate_to * amount, 2)


def symbol_to_currency(symbol):

    symbols = {
        "$": "USD",
        "€": "USD",
        "£": "GBP",
        "¥": "JPY",
        "C$": "CAN",
        "₪": "ILS",
        "₺": "TRY",
        "₱": "PHP",
        "kn": "HRK",
        "Rp": "IDR",
        "฿": "THB",
        "RM": "MYR",
        "zł": "PLN",
        "₽": "RUB",
        "₹": "INR"
    }

    out = symbols.get(symbol)

    if out:

        return out

    return symbol


def save_to_redis(key, data):

    redis_config = {
        'host': 'redis-19487.c55.eu-central-1-1.ec2.cloud.redislabs.com',
        'port': 19487,
        'password': 'VTyUGjlqZwlLmVFdjwMfPDzkO3tGiAsZ',
    }

    try:

        redis = StrictRedis(socket_connect_timeout=3, **redis_config)
        redis.setex(key, 1 * 60, json.dumps(data))

    except Exception:

        print('Error saving data to redis')


def load_from_redis(key):

    data = None

    redis_config = {
        'host': 'redis-19487.c55.eu-central-1-1.ec2.cloud.redislabs.com',
        'port': 19487,
        'password': 'VTyUGjlqZwlLmVFdjwMfPDzkO3tGiAsZ',
    }

    try:

        redis = StrictRedis(socket_connect_timeout=3, **redis_config)
        data = redis.get(key)

    except Exception:

        print("Error loading data from redis")

    if data:

        out = json.loads(data.decode("UTF8"))
        return out

    return None


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--amount", type=float, required='True', help='Amount which we want to convert - float')
    parser.add_argument("--input_currency", type=str, required='True', help='3 letters name or currency symbol')
    parser.add_argument("--output_currency", type=str, help='3 letters name or currency symbol')

    args = parser.parse_args()

    currency_in = args.input_currency
    currency_out = args.output_currency
    amount = args.amount

    if currency_in and amount:

        ret = convert(currency_in, currency_out, amount)

        if ret:
            print(ret)


if __name__ == "__main__":

    main()
