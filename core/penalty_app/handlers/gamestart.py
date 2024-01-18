import random
from aiogram import Router, Bot, F, types, exceptions
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

from django.core.exceptions import ObjectDoesNotExist
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
        chat_member = await bot.get_chat_member(msg.chat.id, msg.from_user.id)
        if chat_member.status in ['administrator', 'creator']:
            game, created = await sync_to_async(Game.objects.get_or_create)(chat_id=msg.chat.id, over=False)
            user, cr = await sync_to_async(TelegramUser.objects.get_or_create)(user_id=msg.from_user.id)
            if not game.owner and created:
                game.owner = user
                game.save()
                players_text = 'Участники: \n'
                builder = InlineKeyboardBuilder()

                builder.add(
                    InlineKeyboardButton(text="Принять участие", callback_data=f"join_{game.id}")
                )

                sent_message = await msg.answer(players_text, reply_markup=builder.as_markup())
                game.message_id = sent_message.message_id
                game.save()
                await awaiting_for_start(msg, game, bot)
            if not game.owner and not created:
                game.delete()
                game = await sync_to_async(Game.objects.create)(chat_id=msg.chat.id, over=False, owner=user)
                players_text = 'Участники: \n'
                builder = InlineKeyboardBuilder()

                builder.add(
                    InlineKeyboardButton(text="Принять участие", callback_data=f"join_{game.id}")
                )

                sent_message = await msg.answer(players_text, reply_markup=builder.as_markup())
                game.message_id = sent_message.message_id
                game.save()
                await awaiting_for_start(msg, game, bot)

            elif game.owner and not created:
                link_to_msg = (
                    f"https://t.me/c/{game.chat_id[4:] if game.chat_id.startswith('-100') else game.chat_id[1:]}/"
                    f"{game.message_id}")
                sent = await msg.answer(f"[Игра уже создана администратором]({link_to_msg})", parse_mode=ParseMode.MARKDOWN)
                await asyncio.sleep(5)
                await bot.delete_message(sent.chat.id, sent.message_id)
                return

        else:
            game, created = await sync_to_async(Game.objects.get_or_create)(chat_id=msg.chat.id, over=False)
            if game.owner:
                await msg.answer("Идёт игра от администратора")
                return
            if game.state == "started":
                await msg.answer("Игра уже в игре")
            if game.state == "collecting" and not created:
                link_to_msg = (
                    f"https://t.me/c/{game.chat_id[4:] if game.chat_id.startswith('-100') else game.chat_id[1:]}/"
                    f"{game.message_id}")
                sent = await msg.answer(f"[Игра уже создана]({link_to_msg})", parse_mode=ParseMode.MARKDOWN)
                await asyncio.sleep(5)
                await bot.delete_message(sent.chat.id, sent.message_id)
                return
            if created:
                players_text = 'Участники: \n'
                builder = InlineKeyboardBuilder()

                builder.add(
                    InlineKeyboardButton(text="Принять участие", callback_data=f"join_{game.id}")
                )

                sent_message = await msg.answer(players_text, reply_markup=builder.as_markup())
                game.message_id = sent_message.message_id
                game.save()
                await awaiting_for_start(msg, game, bot)
    except exceptions.TelegramBadRequest:
        game, created = await sync_to_async(Game.objects.get_or_create)(chat_id=msg.chat.id, over=False)
        if game.owner:
            await msg.answer("Идёт игра от администратора")
            return
        if game.state == "started":
            await msg.answer("Игра уже в игре")
        if game.state == "collecting" and not created:
            link_to_msg = (
                f"https://t.me/c/{game.chat_id[4:] if game.chat_id.startswith('-100') else game.chat_id[1:]}/"
                f"{game.message_id}")
            sent = await msg.answer(f"[Игра уже создана]({link_to_msg})", parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(5)
            await bot.delete_message(sent.chat.id, sent.message_id)
            return
        if created:
            players_text = 'Участники: \n'
            builder = InlineKeyboardBuilder()

            builder.add(
                InlineKeyboardButton(text="Принять участие", callback_data=f"join_{game.id}")
            )

            sent_message = await msg.answer(players_text, reply_markup=builder.as_markup())
            game.message_id = sent_message.message_id
            game.save()
            await awaiting_for_start(msg, game, bot)


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
                InlineKeyboardButton(text="Принять участие", callback_data=f"join_{game.id}")
            )

            # builder.add(
            #     InlineKeyboardButton(text="Принять участие \u2003", url=f"https://t.me/ekz_penaltybot?start={game.id}"))
            await bot.edit_message_text(chat_id=game.chat_id, message_id=game.message_id, text=players_text,
                                        reply_markup=builder.as_markup())


@router.message(Command("extendtime"))
async def extend_time(msg: Message, bot: Bot):
    user, cr = await sync_to_async(TelegramUser.objects.get_or_create)(user_id=msg.from_user.id)
    user.first_name = msg.from_user.first_name
    user.last_name = msg.from_user.last_name
    user.username = msg.from_user.username
    user.save()
    game, created = await sync_to_async(Game.objects.get_or_create)(chat_id=msg.chat.id, over=False)
    if not created and not game.owner:
        game.waiting_time2 += 5
        game.save()
        await msg.answer("Набор игроков продлён на 5 минут")
        players_text = 'Участники: \n\n' + '\n'.join(
            f"{index + 1}. @{player.username if player.username else player.first_name + ' ' + player.last_name}"
            for index, player in enumerate(game.players.all()))
        players_text += f"\n\nОсталось {game.waiting_time2} минут"
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(text="Принять участие", callback_data=f"join_{game.id}")
        )
        # builder.add(InlineKeyboardButton(text="Принять участие", url=f"https://t.me/ekz_penaltybot?start={game.id}"))
        await bot.edit_message_text(chat_id=game.chat_id, message_id=game.message_id, text=players_text,
                                    reply_markup=builder.as_markup(), parse_mode=None)
    if game.owner == user:
        game.waiting_time2 += 5
        game.save()
        await msg.answer("Набор игроков продлён на 5 минут")
        players_text = 'Участники: \n\n' + '\n'.join(
            f"{index + 1}. @{player.username if player.username else player.first_name + ' ' + player.last_name}"
            for index, player in enumerate(game.players.all()))
        players_text += f"\n\nОсталось {game.waiting_time2} минут"
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(text="Принять участие", callback_data=f"join_{game.id}")
        )

        await bot.edit_message_text(chat_id=game.chat_id, message_id=game.message_id, text=players_text,
                                    reply_markup=builder.as_markup(), parse_mode=None)


@router.message(Command("startnow"))
async def start_now(msg: Message, bot: Bot):
    game = await sync_to_async(Game.objects.filter)(chat_id=msg.chat.id, over=False)
    if game:
        game = game.first()
        if game.owner:
            try:
                chat_member = await bot.get_chat_member(msg.chat.id, msg.from_user.id)
                if chat_member.status in ['administrator', 'creator']:
                    game.waiting_time2 = 0
                    game.state = 'started'
                    game.save()
                    await sync_to_async(game.save)()
                    await round_sender(game, bot)
                    return
                else:
                    link_to_msg = (
                        f"https://t.me/c/{game.chat_id[4:] if game.chat_id.startswith('-100') else game.chat_id[1:]}/"
                        f"{game.message_id}")
                    await msg.answer(f"[Игра создана администратором, нет прав для настреок игры]({link_to_msg})",
                                     parse_mode=ParseMode.MARKDOWN)
                    return
            except exceptions.TelegramBadRequest as e:
                print(e)
        if game.state == 'started':
            link_to_msg = (
                f"https://t.me/c/{game.chat_id[4:] if game.chat_id.startswith('-100') else game.chat_id[1:]}/"
                f"{game.message_id}")
            sent = await msg.answer(f"[Игра уже начата]({link_to_msg})", parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(30)
            try:
                await bot.delete_message(sent.chat.id, sent.message_id)
                return
            except Exception as e:
                return e
        elif len(game.players.all()) <= 1:
            sent = await msg.answer("Недостаточно игроков для старта")
            try:
                await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
            except Exception as e:
                print("Выдай права")
            await asyncio.sleep(15)
            await bot.delete_message(sent.chat.id, sent.message_id)
            return

        elif game.state == "collecting" and not game.owner:
            game.waiting_time2 = 0
            game.state = 'started'
            game.save()
            await sync_to_async(game.save)()
            await round_sender(game, bot)

    if not game:
        no_game = "Создайте игру для начала\n/gamestart@ekz_penaltybot"
        no_game = no_game.replace("_", r"\_")
        sent = await msg.answer(no_game)
        await asyncio.sleep(10)
        await bot.delete_message(sent.chat.id, sent.message_id)


@router.callback_query(F.data.startswith("join"))
async def join_button(query: types.CallbackQuery, bot: Bot):
    data = query.data.split("_")
    game = await sync_to_async(Game.objects.get)(id=data[1])
    user, created = await sync_to_async(TelegramUser.objects.get_or_create)(user_id=query.from_user.id)
    user.first_name = query.from_user.first_name
    user.last_name = query.from_user.last_name
    user.username = query.from_user.username
    user.save()

    try:
        game_players = game.players.all()
        if user not in game_players:
            if game.state == "started" and timezone.now() - game.created_time > timezone.timedelta(
                    minutes=30) or game.state == "started" and len(game_players) == 0:
                game.over = True
                game.save()
                await bot.delete_message(game.chat_id, game.message_id)
                return
            if game.state == "collecting":
                game.players.add(user)
                game.save()

                players_text = 'Участники: \n\n' + '\n'.join(f"{index + 1}. {name(player)}"
                                                             for index, player in enumerate(game.players.all()))
                players_text += f"\n\nОсталось {game.waiting_time2} минут"
                builder = InlineKeyboardBuilder()
                builder.add(
                    InlineKeyboardButton(text="Принять участие", callback_data=f"join_{game.id}")
                )
                # builder.add(InlineKeyboardButton(text="Принять участие \u2003",
                #                                  url=f"https://t.me/ekz_penaltybot?start={game.id}"))
                await bot.edit_message_text(chat_id=game.chat_id, message_id=game.message_id, text=players_text,
                                            reply_markup=builder.as_markup())
                chat = await bot.get_chat(game.chat_id)
                await query.answer(f"Вы присоединились к игре в чате {chat.title}")
                return
        elif game.state == "started" and not game.over:
            await query.answer("Игра уже началась")
            return
        elif user in game_players:
            await query.answer("Ты уже в игре, детка!")
            return
    except ObjectDoesNotExist:
        await query.answer('Игра не найдена')


