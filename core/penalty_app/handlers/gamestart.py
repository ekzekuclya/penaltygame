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
from .rounds import round_sender, name


@router.message(Command("gamestart"))
async def start_game_command(msg: Message, state: FSMContext, bot: Bot, command: CommandObject):
    try:
        await msg.delete()
    except Exception as e:
        print("Нет прав", e)
    game, created = await sync_to_async(Game.objects.get_or_create)(chat_id=msg.chat.id, over=False)
    if not created and not game.over:
        if timezone.now() - game.created_time > timezone.timedelta(minutes=30):
            try:
                await bot.delete_message(game.chat_id, game.message_id)
            except Exception as e:
                print("Не удалось удалить")
            game.delete()
            game, created = await sync_to_async(Game.objects.get_or_create)(chat_id=msg.chat.id, over=False)
            players_text = 'Участники: \n'
            builder = InlineKeyboardBuilder()
            builder.add(
                InlineKeyboardButton(text="Принять участие", url=f"https://t.me/ekz_penaltybot?start={game.id}"))

            sent_message = await msg.answer(players_text, reply_markup=builder.as_markup())
            game.message_id = sent_message.message_id
            game.save()
            await awaiting_for_start(msg, game, bot)
            return
        else:
            link_to_msg = (f"https://t.me/c/{game.chat_id[4:] if game.chat_id.startswith('-100') else game.chat_id[1:]}/"
                           f"{game.message_id}")
            sent = await msg.answer(f"[Игра уже создана]({link_to_msg})", parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(5)
            await bot.delete_message(sent.chat.id, sent.message_id)
            return
    game, created = await sync_to_async(Game.objects.get_or_create)(chat_id=msg.chat.id, over=False)
    players_text = 'Участники: \n'
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Принять участие", url=f"https://t.me/ekz_penaltybot?start={game.id}"))

    sent = sent_message = await msg.answer(players_text, reply_markup=builder.as_markup())
    game.message_id = sent_message.message_id
    game.save()
    await awaiting_for_start(msg, game, bot)
    await asyncio.sleep(10)
    try:
        await bot.delete_message(sent.chat.id, sent.message_id)
    except Exception as e:
        return


async def awaiting_for_start(msg, game, bot):
    while True:
        await asyncio.sleep(30)
        game = await sync_to_async(Game.objects.get)(id=game.id)
        if game.state == 'started':
            break
        players = len(game.players.all())

        if game.waiting_time2 <= 0:
            print("[AWAITING_START] WAITING TIME = 0")
            if players >= 2:
                print("[AWAITING_START] ", players)
                await round_sender(game, bot)
                break
        if game.waiting_time2 >= 1:
            game.waiting_time2 -= 1
            game.save()
            players_text = 'Участники: \n\n' + '\n'.join(f"{index + 1}. {name(player)}"
                                                         for index, player in enumerate(game.players.all()))
            players_text += f"\n\nОсталось {game.waiting_time2} минут"
            builder = InlineKeyboardBuilder()
            builder.add(
                InlineKeyboardButton(text="Принять участие \u2003", url=f"https://t.me/ekz_penaltybot?start={game.id}"))
            await bot.edit_message_text(chat_id=game.chat_id, message_id=game.message_id, text=players_text,
                                        reply_markup=builder.as_markup())






# async def awaiting_for_start(msg, game_id, bot):
#     game = await sync_to_async(Game.objects.get)(id=game_id)
#     if game.waiting_time2 in [1, 2, 3, 4, 5, 6, 7, 8]:
#         game.waiting_time2 -= 1
#         await sync_to_async(game.save)()
#         await asyncio.sleep(30)
#         game = await sync_to_async(Game.objects.get)(id=game_id)
#         if game.waiting_time2 == 0:
#             print("ИГРА ДОЛЖНА НАЧАТЬСЯ")
#             chat = await bot.get_chat(game.chat_id)
#             for i in game.players.all():
#                 await bot.send_message(i.user_id, f"Игра в чате {chat.title} началась")
#             game.state = "started"
#             await sync_to_async(game.save)()
#             await round_sender(game, bot)
#             return
#         try:
#             players_text = 'Участники: \n\n' + '\n'.join(
#                 f"{index + 1}. @{player.username if player.username else player.first_name + ' ' + player.last_name}"
#                 for index, player in enumerate(game.players.all()))
#             players_text += f"\n\nОсталось {game.waiting_time2} минут"
#             builder = InlineKeyboardBuilder()
#             builder.add(InlineKeyboardButton(text="Принять участие", url=f"https://t.me/ekz_penaltybot?start={game.id}"))
#             await bot.edit_message_text(chat_id=game.chat_id, message_id=game.message_id, text=players_text,
#                                         reply_markup=builder.as_markup(), parse_mode=None)
#             await awaiting_for_start(msg, game_id, bot)
#             return
#         except Exception as e:
#             await awaiting_for_start(msg, game_id, bot)
#             return
#     elif game.waiting_time2 == 0:
#         if game.state == "started":
#             return
#         print("ИГРА ДОЛЖНА НАЧАТЬСЯ")
#         game.state = "started"
#         await sync_to_async(game.save)()
#         await round_sender(game, bot)


@router.message(Command("extendtime"))
async def extend_time(msg: Message, bot: Bot):
    game, created = await sync_to_async(Game.objects.get_or_create)(chat_id=msg.chat.id)
    if not created and not game.over:
        game.waiting_time2 += 5
        game.save()
        await msg.answer("Набор игроков продлён на 5 минут")
        players_text = 'Участники: \n\n' + '\n'.join(
            f"{index + 1}. @{player.username if player.username else player.first_name + ' ' + player.last_name}"
            for index, player in enumerate(game.players.all()))
        players_text += f"\n\nОсталось {game.waiting_time2} минут"
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="Принять участие", url=f"https://t.me/ekz_penaltybot?start={game.id}"))
        await bot.edit_message_text(chat_id=game.chat_id, message_id=game.message_id, text=players_text,
                                    reply_markup=builder.as_markup(), parse_mode=None)


@router.message(Command("startnow"))
async def start_now(msg: Message, bot: Bot):
    game = await sync_to_async(Game.objects.filter)(chat_id=msg.chat.id, over=False)

    if game:
        game = game.first()
        if len(game.players.all()) <= 1:
            sent = await msg.answer("Недостаточно игроков для старта")
            try:
                await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
            except Exception as e:
                print("Выдай права")
            await asyncio.sleep(15)
            await bot.delete_message(sent.chat.id, sent.message_id)
            return
        game.waiting_time2 = 0
        game.state = 'started'
        game.save()
        await sync_to_async(game.save)()
        await round_sender(game, bot)
        try:
            await msg.delete()
        except Exception as e:
            return

    if not game:
        no_game = "Создайте игру для начала\n/gamestart@ekz_penaltybot"
        no_game = no_game.replace("_", r"\_")
        sent = await msg.answer(no_game)
        await asyncio.sleep(10)
        await bot.delete_message(sent.chat.id, sent.message_id)
    try:
        await msg.delete()
    except Exception as e:
        return






