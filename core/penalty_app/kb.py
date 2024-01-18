from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

come_in = [[InlineKeyboardButton(text='Участвовать', callback_data='come_in')]]
come_in = InlineKeyboardMarkup(inline_keyboard=come_in)


button = [[InlineKeyboardButton(text="go", url='https://t.me/ekz_penaltybot')]]
button = InlineKeyboardMarkup(inline_keyboard=button)


statistic = [[InlineKeyboardButton(text="Статистика", callback_data="stats")]]
statistic = InlineKeyboardMarkup(inline_keyboard=statistic)