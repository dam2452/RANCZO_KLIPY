import logging
from typing import List

from admin_permission_level_factory import AdminPermissionLevelFactory
import aiogram
from moderator_permission_level_factory import ModeratorPermissionLevelFactory
from permission_level_factory import PermissionLevelFactory
from subscribed_permission_level_factory import SubscribedPermissionLevelFactory
from whitelisted_permission_level_factory import WhitelistedPermissionLevelFactory


def create_all_factories(logger: logging.Logger, bot: aiogram.Bot) -> List[PermissionLevelFactory]:
    return [
        AdminPermissionLevelFactory(logger, bot),
        ModeratorPermissionLevelFactory(logger, bot),
        SubscribedPermissionLevelFactory(logger, bot),
        WhitelistedPermissionLevelFactory(logger, bot),
    ]
