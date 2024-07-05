from aiogram import Dispatcher

from bot.handlers.adjust_clip import register_adjust_handler
from bot.handlers.admin_tools import register_admin_handlers
from bot.handlers.bot_start import register_start_command
from bot.handlers.clip_search import register_search_command
from bot.handlers.compile_clips import register_compile_command
from bot.handlers.compile_selected import (
    register_compile_selected_clips_command,
)
from bot.handlers.delete_clip import register_delete_clip_handler
from bot.handlers.episode_list import register_episode_list_handler
from bot.handlers.handle_clip import register_clip_handlers
from bot.handlers.list_clips import register_list_clips_handler
from bot.handlers.manual_clip import register_manual_handler
from bot.handlers.report_issue import register_report_handler
from bot.handlers.save_clip import register_save_handler
from bot.handlers.search_list import register_list_command
from bot.handlers.select_clip import register_select_command
from bot.handlers.send_clip import register_send_clip_handler
from bot.handlers.subscription_status import register_subscription_handler


async def register_handlers(dispatcher: Dispatcher):
    register_compile_selected_clips_command(dispatcher)
    register_adjust_handler(dispatcher)
    register_clip_handlers(dispatcher)
    register_start_command(dispatcher)
    register_search_command(dispatcher)
    register_select_command(dispatcher)
    register_list_command(dispatcher)
    register_compile_command(dispatcher)
    register_admin_handlers(dispatcher)
    register_save_handler(dispatcher)
    register_list_clips_handler(dispatcher)
    register_send_clip_handler(dispatcher)
    register_delete_clip_handler(dispatcher)
    register_episode_list_handler(dispatcher)
    register_subscription_handler(dispatcher)
    register_report_handler(dispatcher)
    register_manual_handler(dispatcher)
    register_delete_clip_handler(dispatcher)
