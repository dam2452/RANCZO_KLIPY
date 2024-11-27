import pytest

import bot.responses.administration.create_key_handler_responses as create_key_msg
import bot.responses.administration.remove_key_handler_responses as remove_key_msg
from bot.tests.base_test import BaseTest


class TestRemoveKeyCommand(BaseTest):

    @pytest.mark.quick
    def test_remove_existing_key(self):
        self.expect_command_result_contains(
            '/addkey 30 tajny_klucz',
            [create_key_msg.get_create_key_success_message(30, "tajny_klucz")],
        )
        self.expect_command_result_contains(
            '/removekey tajny_klucz',
            [remove_key_msg.get_remove_key_success_message("tajny_klucz")],
        )

    @pytest.mark.quick
    def test_remove_nonexistent_key(self):
        self.expect_command_result_contains(
            '/removekey nieistniejacy_klucz',
            [remove_key_msg.get_remove_key_failure_message("nieistniejacy_klucz")],
        )

    @pytest.mark.long
    def test_remove_key_with_special_characters(self):
        self.expect_command_result_contains(
            '/addkey 30 specjalny@klucz#!',
            [create_key_msg.get_create_key_success_message(30, "specjalny@klucz#!")],
        )
        self.expect_command_result_contains(
            '/removekey specjalny@klucz#!',
            [remove_key_msg.get_remove_key_success_message("specjalny@klucz#!")],
        )

    @pytest.mark.long
    def test_remove_key_twice(self):
        self.expect_command_result_contains(
            '/addkey 30 klucz_do_usuniecia',
            [create_key_msg.get_create_key_success_message(30, "klucz_do_usuniecia")],
        )
        self.expect_command_result_contains(
            '/removekey klucz_do_usuniecia',
            [remove_key_msg.get_remove_key_success_message("klucz_do_usuniecia")],
        )
        self.expect_command_result_contains(
            '/removekey klucz_do_usuniecia',
            [remove_key_msg.get_remove_key_failure_message("klucz_do_usuniecia")],
        )
