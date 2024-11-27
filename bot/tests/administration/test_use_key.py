import pytest

import bot.responses.administration.create_key_handler_responses as create_key_msg
import bot.responses.administration.use_key_handler_responses as use_key_msg
from bot.tests.base_test import BaseTest


class TestUseKeyCommand(BaseTest):

    @pytest.mark.quick
    def test_use_existing_key(self):
        self.send_command('/removekey aktywny_klucz')
        self.expect_command_result_contains(
            '/addkey 30 aktywny_klucz',
            [create_key_msg.get_create_key_success_message(30, "aktywny_klucz")],
        )
        self.expect_command_result_contains(
            '/klucz aktywny_klucz',
            [use_key_msg.get_subscription_redeemed_message(30)],
        )
        self.send_command('/removekey aktywny_klucz')

    @pytest.mark.quick
    def test_use_nonexistent_key(self):
        self.expect_command_result_contains(
            '/klucz nieistniejacy_klucz',
            [use_key_msg.get_invalid_key_message()],
        )

    @pytest.mark.long
    def test_use_key_with_special_characters(self):
        self.send_command('/removekey spec@l_key!')
        self.expect_command_result_contains(
            '/addkey 30 spec@l_key!',
            [create_key_msg.get_create_key_success_message(30, "spec@l_key!")],
        )
        self.expect_command_result_contains(
            '/klucz spec@l_key!',
            [use_key_msg.get_subscription_redeemed_message(30)],
        )
        self.send_command('/removekey spec@l_key!')

    @pytest.mark.long
    def test_use_key_twice(self):
        self.send_command('/removekey klucz_jednorazowy')
        self.expect_command_result_contains(
            '/addkey 30 klucz_jednorazowy',
            [create_key_msg.get_create_key_success_message(30, "klucz_jednorazowy")],
        )
        self.expect_command_result_contains(
            '/klucz klucz_jednorazowy',
            [use_key_msg.get_subscription_redeemed_message(30)],
        )
        self.expect_command_result_contains(
            '/klucz klucz_jednorazowy',
            [use_key_msg.get_invalid_key_message()],
        )
        self.send_command('/removekey klucz_jednorazowy')

    @pytest.mark.long
    def test_use_key_without_content(self):
        self.expect_command_result_contains(
            '/klucz',
            [use_key_msg.get_no_message_provided_message()],
        )
