import logging
from typing import List

from bot.factory.admin_permission_level_factory import AdminPermissionLevelFactory
import aiogram
from bot.factory.moderator_permission_level_factory import ModeratorPermissionLevelFactory
from bot.factory.permission_level_factory import PermissionLevelFactory
from bot.factory.subscribed_permission_level_factory import SubscribedPermissionLevelFactory
from bot.factory.whitelisted_permission_level_factory import WhitelistedPermissionLevelFactory


def create_all_factories(logger: logging.Logger, bot: aiogram.Bot) -> List[PermissionLevelFactory]:
    return [
        AdminPermissionLevelFactory(logger, bot),
        ModeratorPermissionLevelFactory(logger, bot),
        SubscribedPermissionLevelFactory(logger, bot),
        WhitelistedPermissionLevelFactory(logger, bot),
    ]
