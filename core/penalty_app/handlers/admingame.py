from aiogram import Router, Bot, types
from aiogram.filters import Command
from aiogram.types import Message
from asgiref.sync import sync_to_async
from ..models import Game
router = Router()


@router.message(Command("admingame"))
async def admin_game(message: Message, bot: Bot, query: types.CallbackQuery):
    user_id = message.from_user.id
    chat_id = message.chat.id

    chat_member = await bot.get_chat_member(chat_id, user_id)

    if chat_member.status in ['administrator', 'creator']:
        current_game = await sync_to_async(Game.objects.filter)(chat_id=message.chat.id, )
    else:
        await message.answer("Вы не являетесь администратором чата.")