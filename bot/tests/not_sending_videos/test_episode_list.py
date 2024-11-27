import pytest
from bot.tests.base_test import BaseTest


class TestEpisodesListsCommand(BaseTest):

    @pytest.mark.quick
    def test_episodes_for_valid_season(self):
        self.expect_command_result_contains('/odcinki 4', ["Szok poporodowy", "Zemsta i wybaczenie"])

    @pytest.mark.quick
    def test_episodes_for_nonexistent_season(self):
        self.expect_command_result_contains('/odcinki 99', ["❌ Nie znaleziono odcinków dla sezonu 99."])
