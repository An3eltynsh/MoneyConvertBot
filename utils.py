import requests
import json
import copy
from config import keyses
from telebot import types


def create_mark(base=None):

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    buttons = []

    for key in keyses.keys():
        if key != base:
            buttons.append(types.KeyboardButton(key.capitalize()))

    markup.add(*buttons)
    return markup


class CurrencyException(Exception):
    pass


class TryExcept:
    @staticmethod
    def try_except_value(value: str) -> str:
        try:
            value_tik = keyses[value.lower()]
            return value_tik
        except KeyError:
            raise CurrencyException(f'Не удалось обработать валюту {value}')

    @staticmethod
    def try_except_amount(value: str) -> float:
        try:
            amount = float(value)
            return amount
        except ValueError:
            raise CurrencyException(f'Не удалось обработать количество {value}')


class CurrencyConvert:
    @staticmethod
    def get_request_ex(base: str, base_tik: str) -> tuple:

        quote = copy.copy(keyses)
        quote.pop(base.lower())

        quote_ = []
        for key in quote.keys():
            quote_.append(quote[key])
        quote_tik = ','.join(quote_)

        api_http = f'https://min-api.cryptocompare.com/data/price?fsym={base_tik}&tsyms={quote_tik}'
        req = requests.get(api_http)
        result = json.loads(req.text)

        return quote, result

    @staticmethod
    def get_request_con(base_tik: str, quote_tik: str, amount: float) -> float:
        api_http = f'https://min-api.cryptocompare.com/data/price?fsym={base_tik}&tsyms={quote_tik}'
        req = requests.get(api_http)
        result = json.loads(req.text)
        print(result)
        return result[quote_tik] * amount

    @staticmethod
    def get_exchange(base: str) -> dict:

        base_tik = TryExcept.try_except_value(base)
        quote, result = CurrencyConvert.get_request_ex(base, base_tik)

        keys_ = quote.keys()
        amount_ = result.values()
        result_dict = dict(zip(keys_, amount_))

        return result_dict

    @staticmethod
    def input_handler(values: str) -> dict:

        result_dict = CurrencyConvert.get_exchange(values.lower())
        return result_dict

    @staticmethod
    def input_handler_conv(base: str, quote: str, amount_: str) -> float:

        if quote == base:
            raise CurrencyException(f'Невозможно перевести одинаковые валюты {base}')

        base_tik = TryExcept.try_except_value(base)
        quote_tik = TryExcept.try_except_value(quote)
        amount = TryExcept.try_except_amount(amount_)

        result = CurrencyConvert.get_request_con(base_tik, quote_tik, amount)
        return result
