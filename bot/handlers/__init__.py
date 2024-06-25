from .clip import register_clip_command
from .expand import register_expand_command
from .select import register_select_command
from .compile import register_compile_command
from .admin import register_admin_handlers
from .search import register_search_handlers
from .start import register_start_handlers
from .save import register_save_handlers

def register_handlers(bot):
    register_clip_command(bot)
    register_expand_command(bot)
    register_select_command(bot)
    register_compile_command(bot)
    register_admin_handlers(bot)
    register_search_handlers(bot)
    register_start_handlers(bot)
    register_save_handlers(bot)
