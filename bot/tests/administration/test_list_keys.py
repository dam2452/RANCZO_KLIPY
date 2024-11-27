import pytest

import bot.responses.administration.list_keys_handler_responses as msg
from bot.tests.base_test import BaseTest


class TestListKeysCommand(BaseTest):

    @pytest.mark.quick
    def test_list_keys_with_keys(self):
        self.expect_command_result_contains(
            '/listkey',
            [msg.create_subscription_keys_response([])],  # Replace with a mock list of keys for testing
        )
