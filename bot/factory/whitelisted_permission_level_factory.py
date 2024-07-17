from bot.factory.permission_level_factory import *  # pylint: disable=wildcard-import, unused-wildcard-import


class WhitelistedPermissionLevelFactory(PermissionLevelFactory):
    def create_handlers(self) -> List[BotMessageHandler]:
        return [
            StartHandler(self._bot, self._logger),
            SubscriptionStatusHandler(self._bot, self._logger),
        ]

    def create_middlewares(self, commands: List[str]) -> List[BotMiddleware]:
        return [
            WhitelistMiddleware(self._logger, commands),
        ]
