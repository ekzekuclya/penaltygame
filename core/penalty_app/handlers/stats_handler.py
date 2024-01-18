from aiogram import Router, F, types, Bot
from asgiref.sync import sync_to_async

from ..models import Chat
router = Router()


@router.callback_query(F.data == "stats")
async def bot_stats(query: types.CallbackQuery, bot: Bot):
    chats = await sync_to_async(Chat.objects.all)()
    stats_text = ""
    for i in chats:
        try:
            chat = await bot.get_chat(i.chat_id)
            stats_text += f"[CHAT] = {chat.title}\n[Колличество участников] = {chat.get_member_count()}"
        except Exception as e:
            print(e)
    await query.message.answer(text=stats_text, parse_mode=None)
