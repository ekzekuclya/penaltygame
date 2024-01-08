import asyncio
import random

from aiogram.types import InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.utils import timezone

from ..models import Round, Game, TelegramUser, Result
from .. import text
from asgiref.sync import sync_to_async
from aiogram import Router, Bot, F, types

router = Router()


async def main_game(game, bot):
    game = await sync_to_async(Game.objects.get)(id=game.id)
    players = list(game.players.all())
    if len(players) >= 2:
        random_players = random.sample(players, 2)
        player1, player2 = random_players[0], random_players[1]
        game_round = await sync_to_async(Round.objects.create)(user1=player1, user2=player2, game=game,
                                                               chat_id=game.chat_id)
        sent = await bot.send_message(chat_id=game_round.chat_id,
                                      text=text.first.format(user1=player1.username, user2=player2.username))
        game_round.message_id = sent.message_id
        game_round.save()
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="🥅", callback_data=f"gameround_{1}_{game.id}_{game_round.id}"))
        builder.add(InlineKeyboardButton(text="🥅", callback_data=f"gameround_{2}_{game.id}_{game_round.id}"))
        builder.add(InlineKeyboardButton(text="🥅", callback_data=f"gameround_{3}_{game.id}_{game_round.id}"))
        builder.adjust(3)
        await bot.send_message(chat_id=player1.user_id, text="Пора сделать ход, ты ловишь мяч", reply_markup=builder.as_markup())
        await bot.send_message(chat_id=player2.user_id, text="Пора сделать ход, ты бьёшь по воротам", reply_markup=builder.as_markup())
        await round_waiter(game_round, game, bot)
    elif len(players) == 1:
        results = await sync_to_async(Result.objects.filter)(game=game)
        result_text = (f"Результаты игры 🔥\n"
                       f"🥇 {players[0].username}\n")
        for i in results:
            if i.position == 2:
                result_text += "🥈 " + str(i.player) + "\n"
            elif i.position == 3:
                result_text += "🥉 " + str(i.player) + "\n"
            else:
                result_text += str(i.position) + " " + str(i.player) + "\n"

        print("ВЫВОДИМ РЕЗУЛЬТАТ ВЫВОДИМ ВЫВОООООДИМ")
        await bot.send_message(chat_id=game.chat_id, text=result_text)
        game.over = True
        game.save()
        return


async def round_waiter(game_round, game, bot):
    print("IN ROUND WAITER")
    game_round = await sync_to_async(Round.objects.get)(id=game_round.id)
    if game_round.waiting_time < timezone.now() and game_round.user1_choice not in [1, 2, 3]:
        game.players.remove(game_round.user1)
        game.save()
        await bot.send_message(chat_id=game_round.user1.user_id, text="Вы исключены за неактивность!")
        await main_game(game, bot)
        return
    if game_round.waiting_time < timezone.now() and game_round.user2_choice not in [1, 2, 3]:
        game.players.remove(game_round.user2)
        game.save()
        await bot.send_message(chat_id=game_round.user2.user_id, text="Вы исключены за неактивность!")
        await main_game(game, bot)
        return
    if game_round.user1_choice in [1, 2, 3] and game_round.user2_choice in [1, 2, 3]:
        players = list(game.players.all())
        if game_round.user1_choice == 1 and game_round.user2_choice == 1:
            for i in text.one_one:
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=game_round.user1, user2=game_round.user2
                ))
                await asyncio.sleep(1)
            if len(players) <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user2, position=len(players))
            game.players.remove(game_round.user2)
            game.save()
        if game_round.user1_choice == 1 and game_round.user2_choice == 2:
            for i in text.one_two:
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=game_round.user1, user2=game_round.user2
                ))
                await asyncio.sleep(1)
            if len(players) <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1, position=len(players))
            game.players.remove(game_round.user1)
            game.save()
        if game_round.user1_choice == 1 and game_round.user2_choice == 3:
            for i in text.one_three:
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=game_round.user1, user2=game_round.user2
                ))
                await asyncio.sleep(1)
            if len(players) <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1, position=len(players))
            game.players.remove(game_round.user1)
            game.save()

        if game_round.user1_choice == 2 and game_round.user2_choice == 1:
            for i in text.two_one:
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=game_round.user1, user2=game_round.user2
                ))
                await asyncio.sleep(1)
            if len(players) <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1, position=len(players))
            game.players.remove(game_round.user1)
            game.save()
        if game_round.user1_choice == 2 and game_round.user2_choice == 2:
            for i in text.two_two:
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=game_round.user1, user2=game_round.user2
                ))
                await asyncio.sleep(1)
            if len(players) <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user2, position=len(players))
            game.players.remove(game_round.user2)
            game.save()
        if game_round.user1_choice == 2 and game_round.user2_choice == 3:
            for i in text.two_three:
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=game_round.user1, user2=game_round.user2
                ))
                await asyncio.sleep(1)
            if len(players) <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1, position=len(players))
            game.players.remove(game_round.user1)
            game.save()
        if game_round.user1_choice == 3 and game_round.user2_choice == 1:
            for i in text.three_one:
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=game_round.user1, user2=game_round.user2
                ))
                await asyncio.sleep(1)
            if len(players) <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1, position=len(players))
            game.players.remove(game_round.user1)
            game.save()
        if game_round.user1_choice == 3 and game_round.user2_choice == 2:
            for i in text.three_two:
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=game_round.user1, user2=game_round.user2
                ))
                await asyncio.sleep(1)
            if len(players) <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1, position=len(players))
            game.players.remove(game_round.user1)
            game.save()
        if game_round.user1_choice == 3 and game_round.user2_choice == 3:
            for i in text.three_three:
                await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
                    user1=game_round.user1, user2=game_round.user2
                ))
                await asyncio.sleep(1)
            if len(players) <= 10:
                result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user2, position=len(players))
            game.players.remove(game_round.user2)
            game.save()
        await main_game(game, bot)
        return
    else:
        print("НИКТО НЕ СДЕЛАЛ ХОД")
        await asyncio.sleep(15)
        await round_waiter(game_round, game, bot)
        return


@router.callback_query(F.data.startswith("gameround"))
async def round_callback(query: types.CallbackQuery):
    data = query.data.split("_")
    print(data)
    # game = await sync_to_async(Game.objects.get)(id=data[2])
    game_round = await sync_to_async(Round.objects.get)(id=data[3])
    user = await sync_to_async(TelegramUser.objects.get)(user_id=query.from_user.id)
    if game_round.user1 == user and game_round.user1_choice is None:
        game_round.user1_choice = data[1]
        game_round.save()
    elif game_round.user2 == user and game_round.user2_choice is None:
        game_round.user2_choice = data[1]
        game_round.save()
    else:
        await query.answer("Вы уже делали ход")






