import pytest

from bot.tests.base_test import BaseTest


class TestEpisodesListsCommand(BaseTest):

    @pytest.mark.quick
    def test_episodes_for_valid_season(self):
        response = self.send_command('/odcinki 4')
        expected_fragments = ["Szok poporodowy","Zemsta i wybaczenie"]
        self.assert_response_contains(response, expected_fragments)

    @pytest.mark.quick
    def test_episodes_for_nonexistent_season(self):
        response = self.send_command('/odcinki 99')
        expected_fragments = ["❌ Nie znaleziono odcinków dla sezonu: 99."]
        self.assert_response_contains(response, expected_fragments)
