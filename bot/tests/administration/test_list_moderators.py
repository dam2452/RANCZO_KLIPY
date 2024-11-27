import pytest

import bot.responses.administration.list_moderators_handler_responses as msg
from bot.tests.base_test import BaseTest


class TestListModeratorsCommand(BaseTest):

    @pytest.mark.quick
    def test_list_moderators_with_moderators(self):
        self.expect_command_result_contains(
            '/listmoderators',
            [msg.format_moderators_list([])],  # Replace with a mock list of moderators for testing
        )
