from aiogram import Router, F, types, Bot
from asgiref.sync import sync_to_async

from ..models import Chat
router = Router()


@router.callback_query(F.data == "stats")
async def bot_stats(query: types.CallbackQuery, bot: Bot):
    chats = await sync_to_async(Chat.objects.all)()
    stats_text = ""
    members = 0
    for i in chats:
        try:
            chat_count = await bot.get_chat_member_count(i.chat_id)
            members += chat_count
        except Exception as e:
            print(e)
    stats_text += f"Колличество чатов = {len(chats)}\nКолличество участников во всех чатах = {members}"
    await query.message.answer(text=stats_text, parse_mode=None)
