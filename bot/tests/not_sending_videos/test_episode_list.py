import pytest

import bot.responses.not_sending_videos.episode_list_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestEpisodesListsCommand(BaseTest):

    @pytest.mark.quick
    def test_episodes_for_valid_season(self):
        self.expect_command_result_contains(
            '/odcinki 4',
            ["Szok poporodowy", "Zemsta i wybaczenie"],
        )

    @pytest.mark.quick
    def test_episodes_for_nonexistent_season(self):
        self.expect_command_result_contains(
            '/odcinki 99',
            [msg.get_no_episodes_found_message(99)],
        )
