# import asyncio
#
# from aiogram import Bot
# from asgiref.sync import sync_to_async
#
# from .rounds import round_sender
# from .. import text
# from ..models import Result, Game, Round
#
#
# async def animation(bot: Bot, game_round):
#     players = len(game_round.game.players.all())
#     game = game_round.game
#     if game_round.user1_choice == 1 and game_round.user2_choice == 1:
#         for i in text.one_one:
#             await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
#                 user1=game_round.user1, user2=game_round.user2
#             ))
#             await asyncio.sleep(1)
#         if players <= 10:
#             result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user2,
#                                                                 position=players)
#         game.players.remove(game_round.user2)
#         game_round.moved = True
#         game.save()
#         game_round.save()
#         await round_sender(game, bot)
#     if game_round.user1_choice == 1 and game_round.user2_choice == 2:
#         for i in text.one_two:
#             await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
#                 user1=game_round.user1, user2=game_round.user2
#             ))
#             await asyncio.sleep(1)
#         if players <= 10:
#             result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1,
#                                                                 position=players)
#         game.players.remove(game_round.user1)
#         game_round.moved = True
#         game.save()
#         game_round.save()
#         await round_sender(game, bot)
#     if game_round.user1_choice == 1 and game_round.user2_choice == 3:
#         for i in text.one_three:
#             await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
#                 user1=game_round.user1, user2=game_round.user2
#             ))
#             await asyncio.sleep(1)
#         if players <= 10:
#             result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1,
#                                                                 position=players)
#         game.players.remove(game_round.user1)
#         game_round.moved = True
#         game.save()
#         game_round.save()
#         await round_sender(game, bot)
#     if game_round.user1_choice == 2 and game_round.user2_choice == 1:
#         for i in text.two_one:
#             await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
#                 user1=game_round.user1, user2=game_round.user2
#             ))
#             await asyncio.sleep(1)
#         if players <= 10:
#             result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1,
#                                                                 position=players)
#         game.players.remove(game_round.user1)
#         game_round.moved = True
#         game.save()
#         game_round.save()
#         await round_sender(game, bot)
#     if game_round.user1_choice == 2 and game_round.user2_choice == 2:
#         for i in text.two_two:
#             await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
#                 user1=game_round.user1, user2=game_round.user2
#             ))
#             await asyncio.sleep(1)
#         if players <= 10:
#             result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user2,
#                                                                 position=players)
#         game.players.remove(game_round.user2)
#         game_round.moved = True
#         game.save()
#         game_round.save()
#         await round_sender(game, bot)
#     if game_round.user1_choice == 2 and game_round.user2_choice == 3:
#         for i in text.two_three:
#             await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
#                 user1=game_round.user1, user2=game_round.user2
#             ))
#             await asyncio.sleep(1)
#         if players <= 10:
#             result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1,
#                                                                 position=players)
#         game.players.remove(game_round.user1)
#         game_round.moved = True
#         game.save()
#         game_round.save()
#         await round_sender(game, bot)
#     if game_round.user1_choice == 3 and game_round.user2_choice == 1:
#         for i in text.three_one:
#             await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
#                 user1=game_round.user1, user2=game_round.user2
#             ))
#             await asyncio.sleep(1)
#         if players <= 10:
#             result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1,
#                                                                 position=players)
#         game.players.remove(game_round.user1)
#         game_round.moved = True
#         game.save()
#         game_round.save()
#         await round_sender(game, bot)
#     if game_round.user1_choice == 3 and game_round.user2_choice == 2:
#         for i in text.three_two:
#             await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
#                 user1=game_round.user1, user2=game_round.user2
#             ))
#             await asyncio.sleep(1)
#         if players <= 10:
#             result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user1,
#                                                                 position=players)
#         game.players.remove(game_round.user1)
#         game_round.moved = True
#         game.save()
#         game_round.save()
#         await round_sender(game, bot)
#     if game_round.user1_choice == 3 and game_round.user2_choice == 3:
#         for i in text.three_three:
#             await bot.edit_message_text(chat_id=game_round.chat_id, message_id=game_round.message_id, text=i.format(
#                 user1=game_round.user1, user2=game_round.user2
#             ))
#             await asyncio.sleep(1)
#         if players <= 10:
#             result = await sync_to_async(Result.objects.create)(game=game, player=game_round.user2,
#                                                                 position=players)
#         game.players.remove(game_round.user2)
#         await sync_to_async(game.save)()
#         game_round.moved = True
#         game.save()
#         game_round.save()
#         await round_sender(game, bot)

