from aiogram import Dispatcher
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
from bot.handlers.shorten import register_shrink_command

def register_handlers(dispatcher: Dispatcher):
    register_clip_command(dispatcher)
    register_expand_command(dispatcher)
    register_start_command(dispatcher)
    register_search_command(dispatcher)
    register_select_command(dispatcher)
    register_list_command(dispatcher)
    register_compile_command(dispatcher)
    register_admin_handlers(dispatcher)
    register_save_handler(dispatcher)
    register_list_clips_handler(dispatcher)
    register_send_clip_handler(dispatcher)
    register_compile_selected_clips_command(dispatcher)
    register_subscription_handler(dispatcher)
    register_shrink_command(dispatcher)

