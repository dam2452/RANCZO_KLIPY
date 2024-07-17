from bot.factory.permission_level_factory import *  # pylint: disable=wildcard-import, unused-wildcard-import


class AdminPermissionLevelFactory(PermissionLevelFactory):
    def create_handlers(self) -> List[BotMessageHandler]:
        return [
            AddSubscriptionHandler(self._bot, self._logger),
            AddWhitelistHandler(self._bot, self._logger),
            RemoveSubscriptionHandler(self._bot, self._logger),
            RemoveWhitelistHandler(self._bot, self._logger),
            UpdateWhitelistHandler(self._bot, self._logger),
        ]

    def create_middlewares(self, commands: List[str]) -> List[BotMiddleware]:
        return [
            AdminMiddleware(self._logger, commands),
        ]
