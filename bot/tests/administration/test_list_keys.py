import pytest

from bot.tests.base_test import BaseTest


class TestListKeysCommand(BaseTest):

    @pytest.mark.quick
    def test_list_keys_with_keys(self):
        self.expect_command_result_contains('/listkey', ["Lista kluczy subskrypcji"])
