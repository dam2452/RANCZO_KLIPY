from bot.factory.permission_level_factory import *  # pylint: disable=wildcard-import, unused-wildcard-import


class ModeratorPermissionLevelFactory(PermissionLevelFactory):
    def create_handlers(self) -> List[BotMessageHandler]:
        return [
            AdminHelpHandler(self._bot, self._logger),
            ListAdminsHandler(self._bot, self._logger),
            ListModeratorsHandler(self._bot, self._logger),
            ListWhitelistHandler(self._bot, self._logger),
            TranscriptionHandler(self._bot, self._logger),
            ListUserMessagesHandler(self._bot, self._logger),
        ]

    def create_middlewares(self, commands: List[str]) -> List[BotMiddleware]:
        return [
            ModeratorMiddleware(self._logger, commands),
        ]
