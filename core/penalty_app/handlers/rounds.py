import asyncio
import random

from aiogram import Router, types, F, Bot
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

from ..models import Round, Game, TelegramUser, Result
from .. import text
from aiogram.fsm.state import StatesGroup, State

router = Router()


def name(user):
    link = "tg://user?id="
    player_username = (
        f"@{user.username}"
        if user.username
        else (
            f"[{user.first_name + (' ' + user.last_name if user.last_name else '')}]"
            f"({link}{str(user.user_id)})"
        )
    )
    player_username = player_username.replace("_", r"\_")
    return "👤 " + player_username


async def round_sender(game, bot):
    game = await sync_to_async(Game.objects.get)(id=game.id)
    players = list(game.players.all())
    if len(players) >= 2:
        random_players = random.sample(players, 2)
        player1, player2 = random_players[0], random_players[1]
        game_round = await sync_to_async(Round.objects.create)(user1=player1, user2=player2, game=game,
                                                               chat_id=game.chat_id)

        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="🥅", callback_data=f"gameround_{1}_{game.id}_{game_round.id}"))
        builder.add(InlineKeyboardButton(text="🥅", callback_data=f"gameround_{2}_{game.id}_{game_round.id}"))
        builder.add(InlineKeyboardButton(text="🥅", callback_data=f"gameround_{3}_{game.id}_{game_round.id}"))
        builder.adjust(3)

        sent = await bot.send_message(chat_id=game_round.chat_id, text=text.first.format(user1=name(game_round.user1),
                                                                                         user2=name(game_round.user2)),
                                      reply_markup=builder.as_markup(), parse_mode=ParseMode.MARKDOWN)
        game_round.message_id = sent.message_id
        game_round.save()
        await kick_afk(game_round, bot)
        await asyncio.sleep(30)
        await bot.delete_message(chat_id=game_round.chat_id, message_id=game_round.message_id)

    elif len(players) == 1 and not game.over:
        results = await sync_to_async(Result.objects.filter)(game=game)
        result_text = (f"Результаты игры 🔥\n"
                       f"🥇 {name(players[0])}\n")
        for i in results:
            if i.position == 2:
                result_text += "🥈 " + str(name(i.player)) + "\n"
            elif i.position == 3:
                result_text += "🥉 " + str(name(i.player)) + "\n"
            else:
                result_text += str(i.position) + " " + str(name(i.player)) + "\n"

        print("ВЫВОДИМ РЕЗУЛЬТАТ ВЫВОДИМ ВЫВОООООДИМ")
        await bot.send_message(chat_id=game.chat_id, text=result_text)
        game.over = True
        game.save()
        try:
            await bot.delete_message(chat_id=game.chat_id, message_id=game.message_id)
        except Exception as e:
            return
        return


def round_bool(game_round):
    game_round = Round.objects.get(id=game_round.id)
    choices = [1, 2, 3]
    return True if game_round.user1_choice in choices and game_round.user2_choice in choices else False


async def kick_afk(game_round, bot):
    while True:
        game_round = await sync_to_async(Round.objects.get)(id=game_round.id)
        game_round.waiting_time2 -= 1
        game_round.save()
        print("IN KICK AFK")
        await asyncio.sleep(10)
        game_round = await sync_to_async(Round.objects.get)(id=game_round.id)
        try:
            game = await sync_to_async(Game.objects.get)(id=game_round.game.id)
            choices = [1, 2, 3]
            if game_round.moved:
                print("KICK AFK BREAK")
                break
            if game_round.waiting_time2 <= 0 and game_round.user2_choice not in choices:
                game.players.remove(game_round.user2)
                print("kick user 2")
                game.save()
            if game_round.waiting_time2 <= 0 and game_round.user1_choice not in choices:
                game.players.remove(game_round.user1)
                print('kick user 1')
                game.save()
            if game_round.waiting_time2 <= 0:
                if game_round.user2_choice not in choices or game_round.user1_choice not in choices:
                    await round_sender(game_round.game, bot)
                    break
        except ObjectDoesNotExist:
            await bot.send_message(game_round.chat_id, "Администратор отменил игру")


async def animation(bot, game_round):
    print("IN ANIMATION")
    players = len(game_round.game.players.all())
    game = await sync_to_async(Game.objects.get)(id=game_round.game.id)
    game_round = await sync_to_async(Round.objects.get)(id=game_round.id)
    print("CHOICE USER 1", game_round.user1_choice)
    print("CHOICE USER 2", game_round.user2_choice)
    name_user1 = name(game_round.user1)
    name_user2 = name(game_round.user2)
    sleep = 0.3
    a = 0
    if game_round.user1_choice == 1 and game_round.user2_choice == 1:
        print("IN 1:1")
        try:
            for i in text.one_one:
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=name_user1, user2=name_user2
                ))
                a += 1
                await asyncio.sleep(sleep)
            if players <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user2,
                                                                    position=players)
            game.players.remove(game_round.user2)
            game_round.moved = True
            game.save()
            game_round.save()
            await round_sender(game, bot)
        except Exception as e:
            await asyncio.sleep(5)
            for i in text.one_one[a:]:
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=name_user1, user2=name_user2
                ))
                a += 1
                await asyncio.sleep(1)
            if players <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user2,
                                                                    position=players)
            game.players.remove(game_round.user2)
            game_round.moved = True
            game.save()
            game_round.save()
            await round_sender(game, bot)
    if game_round.user1_choice == 1 and game_round.user2_choice == 2:
        try:
            for i in text.one_two:
                a += 1
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=name_user1, user2=name_user2
                ))
                await asyncio.sleep(sleep)
            if players <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1,
                                                                    position=players)
            game.players.remove(game_round.user1)

            game_round.moved = True
            game.save()
            game_round.save()
            await round_sender(game, bot)
        except Exception as e:
            for i in text.one_two[a:]:
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=name_user1, user2=name_user2
                ))
                await asyncio.sleep(1)
            if players <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1,
                                                                    position=players)
            game.players.remove(game_round.user1)

            game_round.moved = True
            game.save()
            game_round.save()
            await round_sender(game, bot)
    if game_round.user1_choice == 1 and game_round.user2_choice == 3:
        try:
            for i in text.one_three:
                a += 1
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=name_user1, user2=name_user2
                ))
                await asyncio.sleep(sleep)
            if players <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1,
                                                                    position=players)
            game.players.remove(game_round.user1)
            game_round.moved = True
            game.save()
            game_round.save()
            await round_sender(game, bot)
        except Exception as e:
            for i in text.one_three[a:]:
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=name_user1, user2=name_user2
                ))
                await asyncio.sleep(1)
            if players <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1,
                                                                    position=players)
            game.players.remove(game_round.user1)
            game_round.moved = True
            game.save()
            game_round.save()
            await round_sender(game, bot)
    if game_round.user1_choice == 2 and game_round.user2_choice == 1:
        try:
            for i in text.two_one:
                a += 1
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=name_user1, user2=name_user2
                ))
                await asyncio.sleep(sleep)
            if players <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1,
                                                                    position=players)
            game.players.remove(game_round.user1)
            game_round.moved = True
            game.save()
            game_round.save()
            await round_sender(game, bot)
        except Exception as e:
            for i in text.two_one[a:]:
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=name_user1, user2=name_user2
                ))
                await asyncio.sleep(1)
            if players <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1,
                                                                    position=players)
            game.players.remove(game_round.user1)
            game_round.moved = True
            game.save()
            game_round.save()
            await round_sender(game, bot)
    if game_round.user1_choice == 2 and game_round.user2_choice == 2:
        try:
            for i in text.two_two:
                a += 1
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=name_user1, user2=name_user2
                ))
                await asyncio.sleep(sleep)
            if players <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user2,
                                                                    position=players)
            game.players.remove(game_round.user2)
            game_round.moved = True
            game.save()
            game_round.save()
            await round_sender(game, bot)
        except Exception as e:
            for i in text.two_two[a:]:
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=name_user1, user2=name_user2
                ))
                await asyncio.sleep(1)
            if players <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user2,
                                                                    position=players)
            game.players.remove(game_round.user2)
            game_round.moved = True
            game.save()
            game_round.save()
            await round_sender(game, bot)
    if game_round.user1_choice == 2 and game_round.user2_choice == 3:
        try:
            for i in text.two_three:
                a += 1
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=name_user1, user2=name_user2
                ))
                await asyncio.sleep(sleep)
            if players <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1,
                                                                    position=players)
            game.players.remove(game_round.user1)
            game_round.moved = True
            game.save()
            game_round.save()
            await round_sender(game, bot)
        except Exception as e:
            for i in text.two_three[a:]:
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=name_user1, user2=name_user2
                ))
                await asyncio.sleep(1)
            if players <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1,
                                                                    position=players)
            game.players.remove(game_round.user1)
            game_round.moved = True
            game.save()
            game_round.save()
            await round_sender(game, bot)
    if game_round.user1_choice == 3 and game_round.user2_choice == 1:
        try:
            for i in text.three_one:
                a += 1
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=name_user1, user2=name_user2
                ))
                await asyncio.sleep(sleep)
            if players <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1,
                                                                    position=players)
            game.players.remove(game_round.user1)
            game_round.moved = True
            game.save()
            game_round.save()
            await round_sender(game, bot)
        except Exception as e:
            for i in text.three_one[a:]:
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=name_user1, user2=name_user2
                ))
                await asyncio.sleep(1)
            if players <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1,
                                                                    position=players)
            game.players.remove(game_round.user1)
            game_round.moved = True
            game.save()
            game_round.save()
            await round_sender(game, bot)
    if game_round.user1_choice == 3 and game_round.user2_choice == 2:
        try:
            for i in text.three_two:
                a += 1
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=name_user1, user2=name_user2
                ))
                await asyncio.sleep(sleep)
            if players <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1,
                                                                    position=players)
            game.players.remove(game_round.user1)
            game_round.moved = True
            game.save()
            game_round.save()
            await round_sender(game, bot)
        except Exception as e:
            for i in text.three_two[a:]:
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=name_user1, user2=name_user2
                ))
                await asyncio.sleep(1)
            if players <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1,
                                                                    position=players)
            game.players.remove(game_round.user1)
            game_round.moved = True
            game.save()
            game_round.save()
            await round_sender(game, bot)
    if game_round.user1_choice == 3 and game_round.user2_choice == 3:
        try:
            for i in text.three_three:
                a += 1
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=name_user1, user2=name_user2
                ))
                await asyncio.sleep(sleep)
            if players <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user2,
                                                                    position=players)
            game.players.remove(game_round.user2)
            game.save()
            game_round.moved = True
            game_round.save()
            await round_sender(game, bot)
        except Exception as e:
            for i in text.three_three[a:]:
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=name_user1, user2=name_user2
                ))
                await asyncio.sleep(1)
            if players <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user2,
                                                                    position=players)
            game.players.remove(game_round.user2)
            game.save()
            game_round.moved = True
            game_round.save()
            await round_sender(game, bot)

async def rounder(game_round, game, bot):
    move = round_bool(game_round)
    print("MOVE", move)

    if move:
        game_round = await sync_to_async(Round.objects.get)(id=game_round.id)
        if not game_round.moved:
            await animation(bot, game_round)
            return


@router.callback_query(F.data.startswith("gameround"))
async def round_callback(query: types.CallbackQuery, bot: Bot):
    data = query.data.split("_")
    print(data)
    game = await sync_to_async(Game.objects.get)(id=data[2])
    game_round = await sync_to_async(Round.objects.get)(id=data[3])
    user = await sync_to_async(TelegramUser.objects.get)(user_id=query.from_user.id)
    target_user = game_round.user2
    print("USER 2 = USER 2", game_round.user2 == user)
    print(target_user.username, user.username)
    print(game_round.user2_choice)
    if game_round.user1 == user and not game_round.user1_choice:
        game_round.user1_choice = data[1]
        game_round.save()
        await rounder(game_round, game, bot)
    elif game_round.user2 == user and not game_round.user2_choice:
        game_round.user2_choice = data[1]
        game_round.save()
        await rounder(game_round, game, bot)
    elif game_round.user1 != user and game_round.user2 != user:
        await query.answer("Сейчас не ваш ход")
    else:
        await query.answer("Вы уже делали ход")





