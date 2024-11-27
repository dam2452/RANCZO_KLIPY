import pytest

import bot.responses.administration.start_handler_responses as msg
from bot.tests.base_test import BaseTest


class TestStartCommand(BaseTest):

    @pytest.mark.quick
    def test_start_base_commands(self):
        self.expect_command_result_contains('/start', [msg.get_basic_message()])

    @pytest.mark.quick
    def test_start_invalid_command(self):
        self.expect_command_result_contains('/start nieistniejace_polecenie', [msg.get_invalid_command_message()])

    @pytest.mark.long
    def test_start_search_commands(self):
        self.expect_command_result_contains('/start wyszukiwanie', [msg.get_search_message()])

    @pytest.mark.long
    def test_start_edit_commands(self):
        self.expect_command_result_contains('/start edycja', [msg.get_edit_message()])

    @pytest.mark.long
    def test_start_management_commands(self):
        self.expect_command_result_contains('/start zarzadzanie', [msg.get_menagement_message()])

    @pytest.mark.long
    def test_start_reporting_command(self):
        self.expect_command_result_contains('/start raportowanie', [msg.get_reporting_message()])

    @pytest.mark.long
    def test_start_subscription_command(self):
        self.expect_command_result_contains('/start subskrypcje', [msg.get_subscriptions_message()])

    @pytest.mark.long
    def test_start_all_commands(self):
        self.expect_command_result_contains('/start wszystko', [msg.get_all_message()])

    @pytest.mark.long
    def test_start_shortcuts(self):
        self.expect_command_result_contains('/start skroty', [msg.get_shortcuts_message()])
