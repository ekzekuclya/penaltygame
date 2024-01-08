from aiogram import Router, Bot
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.utils import timezone

from ..models import Game, TelegramUser
from asgiref.sync import sync_to_async

router = Router()


@router.message(Command("start"))
async def start_command(msg: Message, state: FSMContext, bot: Bot, command: CommandObject):
    game_id = command.args
    user, created = await sync_to_async(TelegramUser.objects.get_or_create)(user_id=msg.from_user.id)
    user.first_name = msg.from_user.first_name
    user.last_name = msg.from_user.last_name
    user.username = msg.from_user.username
    user.save()
    if game_id:
        game = await sync_to_async(Game.objects.get)(id=game_id)
        game_players = game.players.all()
        if user not in game_players and game.state == "collecting":
            game.players.add(user)
            game.save()
            players_text = 'Участники: \n\n' + '\n'.join(f"{index + 1}. @{player.username}"
                                                         for index, player in enumerate(game.players.all()))
            time_difference = game.waiting_time - timezone.now()
            minutes_until_start = int(time_difference.total_seconds() // 60)
            players_text += f"\n\nДо начала игры осталось {minutes_until_start} минут"
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text="Принять участие", url=f"https://t.me/ekz_penaltybot?start={game.id}"))
            await bot.edit_message_text(chat_id=game.chat_id, message_id=game.message_id, text=players_text,
                                        reply_markup=builder.as_markup(), parse_mode=None)
            chat = await bot.get_chat(game.chat_id)
            await msg.answer(f"Вы присоединились к игре в чате {chat.title}")
            return
        elif game.state == "started" and not game.over:
            await msg.answer("Игра уже началась")
            return
        elif user in game_players:
            await msg.answer("Ты уже в игре, детка!")
            return
    await msg.answer("ДЕТКА БЕЙБИ, БОТ ГОТОВИТСЯ, СКОРО ВСЁ НАЧНЁТСЯ!!!")
