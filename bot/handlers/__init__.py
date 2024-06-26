from aiogram import Dispatcher
from .clip import register_clip_command
from .start import register_start_command
from  .expand import register_expand_command
from .search import register_search_command
from .select import register_select_command
from .list import register_list_command


def register_handlers(dispatcher: Dispatcher):
    register_clip_command(dispatcher)
    register_expand_command(dispatcher)
    register_start_command(dispatcher)
    register_search_command(dispatcher)
    register_select_command(dispatcher)
    register_list_command(dispatcher)
