from aiogram import Router, Bot
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.utils import timezone

from .rounds import name
from ..models import Game, TelegramUser
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
router = Router()


@router.message(Command("start"))
async def start_command(msg: Message, state: FSMContext, bot: Bot, command: CommandObject):
    game_id = command.args
    user, created = await sync_to_async(TelegramUser.objects.get_or_create)(user_id=msg.from_user.id)
    user.first_name = msg.from_user.first_name
    user.last_name = msg.from_user.last_name
    user.username = msg.from_user.username
    user.save()
    print(game_id)
    if game_id:
        game = await sync_to_async(Game.objects.get)(id=game_id)
        game_players = game.players.all()
        if user not in game_players:
            if game.state == "started" and timezone.now() - game.created_time > timezone.timedelta(minutes=30) or game.state == "started" and len(game_players) == 0:
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
                builder.add(InlineKeyboardButton(text="Принять участие \u2003", url=f"https://t.me/ekz_penaltybot?start={game.id}"))
                await bot.edit_message_text(chat_id=game.chat_id, message_id=game.message_id, text=players_text,
                                                reply_markup=builder.as_markup())
                chat = await bot.get_chat(game.chat_id)
                await msg.answer(f"Вы присоединились к игре в чате {chat.title}")
                return
        elif game.state == "started" and not game.over:
            await msg.answer("Игра уже началась")
            return
        elif user in game_players:
            await msg.answer("Ты уже в игре, детка!")
            return



