import pytest

from bot.tests.base_test import BaseTest


class TestListModeratorsCommand(BaseTest):

    @pytest.mark.quick
    def test_list_moderators_with_moderators(self):
        response = self.send_command('/listmoderators')
        expected_fragments = ["Lista moderatorów:"]
        self.assert_response_contains(response, expected_fragments)
