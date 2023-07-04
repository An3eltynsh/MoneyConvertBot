import telebot
import traceback
import os
from emoji import emojize
from config import keyses
from utils import CurrencyConvert
from utils import CurrencyException
from utils import create_mark
from dotenv import load_dotenv
from dotenv import find_dotenv

load_dotenv(find_dotenv())

bot = telebot.TeleBot(os.getenv('TOKEN'))


@bot.message_handler(commands=['start', 'help'])
def start(message: telebot.types.Message):
    text = f'{emojize(":robot:")} Что умеет бот: \n\n{emojize(":bookmark_tabs:")} '\
        'Чтобы увидеть список доступных валют введите комманду: /values'\
        f'\n\n{emojize(":chart_increasing:")} Чтобы посмотреть курс выбранной '\
        'валюты к другим валютам введите комманду: /exchange ' \
        f'\n\n{emojize(":money_with_wings:")} Чтобы перевести сумму из одной валюты в '\
        'другую введите комманду: /convert'
    bot.reply_to(message, text)


@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = f'{emojize(":bookmark_tabs:")} Список доступных валют:\n'
    for key in keyses.keys():
        text += '\n' + f'{emojize(":small_blue_diamond:")}' + f'{key}'
    bot.reply_to(message, text)


@bot.message_handler(commands=['exchange'])
def exchange_rates(message: telebot.types.Message):
    text = 'Выберите валюту, чтобы посмотреть ее курс к другим валютам:'
    bot.send_message(message.chat.id, text, reply_markup=create_mark())
    bot.register_next_step_handler(message, base_ex_handler)


def base_ex_handler(message: telebot.types.Message):

    base = message.text.strip()

    try:
        result_dict = CurrencyConvert.input_handler(base)

    except CurrencyException as e:
        bot.reply_to(message, f'Ошибка в команде: \n{e}')
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        bot.reply_to(message, f'Неизвестная ошибка: \n{e}')

    else:
        text = f'Курс: \nодин {base.lower()} к\n'
        for key in result_dict.keys():
            text += f'{emojize(":small_blue_diamond:")} {key} - {result_dict[key]}\n'
        bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['convert'])
def convert_rates(message: telebot.types.Message):
    text = 'Выберите валюту:'
    bot.send_message(message.chat.id, text, reply_markup=create_mark())
    bot.register_next_step_handler(message, base_con_handler)


def base_con_handler(message: telebot.types.Message):
    base = message.text.strip()
    text = 'Выберите валюту в которую будем переводить:'
    bot.send_message(message.chat.id, text, reply_markup=create_mark())
    bot.register_next_step_handler(message, quote_con_handler, base)


def quote_con_handler(message: telebot.types.Message, base):
    quote = message.text.strip()
    text = 'Напишите колличество переводимой валюты:'
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, amount_con_handler, base, quote)


def amount_con_handler(message: telebot.types.Message, base, quote):

    amount = message.text.strip()

    try:
        result = CurrencyConvert.input_handler_conv(base, quote, amount)

    except CurrencyException as e:
        bot.reply_to(message, f'Ошибка в команде: \n{e}')
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        bot.reply_to(message, f'Неизвестная ошибка: \n{e}')

    else:
        text = f'{emojize(":money_with_wings:")} Цена {amount} {base.lower()} в {quote.lower()} - {result}'
        bot.send_message(message.chat.id, text)


bot.polling()
