from aiogram import Dispatcher

from bot.handlers_old.adjust_clip import register_adjust_handler
from bot.handlers_old.admin_tools import register_admin_handlers
from bot.handlers_old.bot_start import register_start_command
from bot.handlers_old.clip_search import register_search_command
from bot.handlers_old.compile_clips import register_compile_command
from bot.handlers_old.compile_selected import register_compile_selected_clips_command
from bot.handlers_old.delete_clip import register_delete_clip_handler
from bot.handlers_old.episode_list import register_episode_list_handler
from bot.handlers_old.handle_clip import register_clip_handlers
from bot.handlers_old.list_clips import register_list_clips_handler
from bot.handlers_old.manual_clip import register_manual_handler
from bot.handlers_old.report_issue import register_report_handler
from bot.handlers_old.save_clip import register_save_handler
from bot.handlers_old.search_list import register_list_command
from bot.handlers_old.select_clip import register_select_command
from bot.handlers_old.send_clip import register_send_clip_handler
from bot.handlers_old.subscription_status import register_subscription_handler


async def register_handlers(dispatcher: Dispatcher) -> None:
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
