from bot.factory.permission_level_factory import *  # pylint: disable=wildcard-import, unused-wildcard-import


class SubscribedPermissionLevelFactory(PermissionLevelFactory):
    def create_handlers(self) -> List[BotMessageHandler]:
        return [
            AdjustVideoClipHandler(self._bot, self._logger),
            ClipHandler(self._bot, self._logger),
            CompileClipsHandler(self._bot, self._logger),
            CompileSelectedClipsHandler(self._bot, self._logger),
            DeleteClipHandler(self._bot, self._logger),
            EpisodeListHandler(self._bot, self._logger),
            ManualClipHandler(self._bot, self._logger),
            MyClipsHandler(self._bot, self._logger),
            ReportIssueHandler(self._bot, self._logger),
            SaveClipHandler(self._bot, self._logger),
            SearchHandler(self._bot, self._logger),
            SearchListHandler(self._bot, self._logger),
            SelectClipHandler(self._bot, self._logger),
            SendClipHandler(self._bot, self._logger),
        ]

    def create_middlewares(self, commands: List[str]) -> List[BotMiddleware]:
        return [
            SubscriberMiddleware(self._logger, commands),
        ]
