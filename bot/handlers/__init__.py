from aiogram import Router, Dispatcher
from bot.handlers.clip import register_clip_command
from bot.handlers.start import register_start_command
from bot.handlers.expand import register_expand_command
from bot.handlers.search import register_search_command
from bot.handlers.select import register_select_command
from bot.handlers.list import register_list_command
from bot.handlers.compile import register_compile_command
from bot.handlers.admin import register_admin_handlers
from bot.handlers.save import register_save_handler
from bot.handlers.list_saved_clips import register_list_clips_handler
from bot.handlers.send_saved_clip import register_send_clip_handler
from bot.handlers.compile_selected_clips import register_compile_selected_clips_command
from bot.handlers.subscription import register_subscription_handler
from bot.handlers.report import register_report_handler
from bot.handlers.delete_clip import register_delete_clip_handler
# from bot.handlers.shorten import register_shorten_handler

async def register_handlers(dispatcher: Dispatcher):
    router = Router()

    register_clip_command(router)
    register_expand_command(router)
    register_start_command(router)
    register_search_command(router)
    register_select_command(router)
    register_list_command(router)
    register_compile_command(router)
    register_admin_handlers(router)
    register_save_handler(router)
    register_list_clips_handler(router)
    register_send_clip_handler(router)
    register_compile_selected_clips_command(router)
    register_subscription_handler(router)
    register_report_handler(router)
    register_delete_clip_handler(router)
    # register_shorten_handler(router)
    dispatcher.include_router(router)
