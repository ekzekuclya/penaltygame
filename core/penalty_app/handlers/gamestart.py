import random
from aiogram import Router, Bot, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
from django.utils import timezone
from ..models import Game, TelegramUser, Round
from asgiref.sync import sync_to_async
from .. import kb
router = Router()
from .. import text
from .maingame import main_game


@router.message(Command("gamestart"))
async def start_game_command(msg: Message, state: FSMContext, bot: Bot, command: CommandObject):
    game, created = await sync_to_async(Game.objects.get_or_create)(chat_id=msg.chat.id, over=False)
    if not created and not game.over:
        link_to_msg = (f"https://t.me/c/{game.chat_id[4:] if game.chat_id.startswith('-100') else game.chat_id[1:]}/"
                       f"{game.message_id}")
        try:
            await msg.answer(f"[Игра уже создана]({link_to_msg})", parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            print(e)
            await msg.answer("Игра уже создана")
        return
    players_text = 'Участники: \n\nДо начала игры осталось 10 минут'
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Принять участие", url=f"https://t.me/ekz_penaltybot?start={game.id}"))
    sent_message = await msg.answer(players_text, reply_markup=builder.as_markup())
    game.message_id = sent_message.message_id
    game.save()
    await awaiting_for_start(msg, game.id, bot)


async def awaiting_for_start(msg, game_id, bot):
    game = await sync_to_async(Game.objects.get)(id=game_id)
    if game.waiting_time > timezone.now():
        print("ЕЩЕ ЖДЁМ")
        print(game.waiting_time)
        print(timezone.now())
        await asyncio.sleep(60)
        try:
            players_text = 'Участники: \n\n' + '\n'.join(
                f"{index + 1}. @{player.username if player.username else player.first_name + ' ' + player.last_name}"
                for index, player in enumerate(game.players.all()))
            minutes_until_start = int(time_until_start(game).total_seconds() // 60)
            players_text += f"\n\nОсталось {minutes_until_start} минут"
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text="Принять участие", url=f"https://t.me/ekz_penaltybot?start={game.id}"))
            await bot.edit_message_text(chat_id=game.chat_id, message_id=game.message_id, text=players_text,
                                        reply_markup=builder.as_markup(), parse_mode=None)
            await awaiting_for_start(msg, game_id, bot)
            return
        except Exception as e:
            await awaiting_for_start(msg, game_id, bot)
            return
    elif game.waiting_time < timezone.now():
        print("ИГРА ДОЛЖНА НАЧАТЬСЯ")
        chat = await bot.get_chat(game.chat_id)
        for i in game.players.all():
            await bot.send_message(i.user_id, f"Игра в чате {chat.title} началась")
        game.state = "started"
        game.save()
        await main_game(game, bot)


@router.message(Command("extendtime"))
async def extend_time(msg: Message, bot: Bot):
    game, created = await sync_to_async(Game.objects.get_or_create)(chat_id=msg.chat.id)
    if not created and not game.over:
        game.waiting_time += timezone.timedelta(minutes=5)
        game.save()
        await msg.answer("Набор игроков продлён на 5 минут")
        players_text = 'Участники: \n\n' + '\n'.join(
            f"{index + 1}. @{player.username if player.username else player.first_name + ' ' + player.last_name}"
            for index, player in enumerate(game.players.all()))
        minutes_until_start = int(time_until_start(game).total_seconds() // 60)
        players_text += f"\n\nОсталось {minutes_until_start} минут"
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="Принять участие", url=f"https://t.me/ekz_penaltybot?start={game.id}"))
        await bot.edit_message_text(chat_id=game.chat_id, message_id=game.message_id, text=players_text,
                                    reply_markup=builder.as_markup(), parse_mode=None)


def time_until_start(game):
    time_difference = game.waiting_time - timezone.now()
    if time_difference.total_seconds() < 0:
        return timezone.timedelta()
    return time_difference


@router.message(Command("playground"))
async def main4_game(msg: Message, bot: Bot):
    a = await msg.answer(text.first.format(user1=msg.from_user.username, user2=msg.from_user.username))
    for i in text.one_one:
        await asyncio.sleep(1)
        await bot.edit_message_text(chat_id=a.chat.id, message_id=a.message_id, text=i.format(
            user1=msg.from_user.username, user2=msg.from_user.username))


@router.message(Command("playground2"))
async def main2_game(msg: Message, bot: Bot):

    a = await msg.answer(text.frame1.format(user1=msg.from_user.username, user2=msg.from_user.username))
    for i in text.my_listt:
        await asyncio.sleep(0.3)
        await bot.edit_message_text(chat_id=a.chat.id, message_id=a.message_id, text=i.format(user=msg.from_user.username))

