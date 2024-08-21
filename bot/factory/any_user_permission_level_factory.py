from bot.factory.permission_level_factory import *  # pylint: disable=wildcard-import, unused-wildcard-import


class AnyUserPermissionLevelFactory(PermissionLevelFactory):
    def create_handlers(self) -> List[BotMessageHandler]:
        return [
            SaveUserInfoHandler(self._bot, self._logger),
        ]

    def create_middlewares(self, commands: List[str]) -> List[BotMiddleware]:
        # Brak middleware, ponieważ każdy może używać tych komend
        return []
