import pytest

from bot.tests.base_test import BaseTest


class TestStartCommand(BaseTest):

    @pytest.mark.quick
    def test_start_base_commands(self):
        self.expect_command_result_contains('/start', ["Podstawowe komendy"])

    @pytest.mark.quick
    def test_start_invalid_command(self):
        self.expect_command_result_contains('/start nieistniejace_polecenie', ["Niepoprawna komenda"])

    @pytest.mark.long
    def test_start_search_commands(self):
        self.expect_command_result_contains(
            '/start wyszukiwanie',
            ["/klip", "/szukaj", "/lista", "/wybierz", "/odcinki", "/wytnij"]
        )

    @pytest.mark.long
    def test_start_edit_commands(self):
        self.expect_command_result_contains('/start edycja', ["/dostosuj", "/kompiluj"])

    @pytest.mark.long
    def test_start_management_commands(self):
        self.expect_command_result_contains(
            '/start zarzadzanie',
            ["/zapisz", "/mojeklipy", "/wyslij", "/polaczklipy", "/usunklip"]
        )

    @pytest.mark.long
    def test_start_reporting_command(self):
        self.expect_command_result_contains('/start raportowanie', ["/report"])

    @pytest.mark.long
    def test_start_subscription_command(self):
        self.expect_command_result_contains('/start subskrypcje', ["/subskrypcja"])

    @pytest.mark.long
    def test_start_all_commands(self):
        self.expect_command_result_contains(
            '/start wszystko',
            [
                "/klip", "/szukaj", "/lista", "/wybierz", "/odcinki", "/wytnij",
                "/dostosuj", "/kompiluj", "/zapisz", "/mojeklipy", "/wyslij",
                "/polaczklipy", "/usunklip", "/report", "/subskrypcja",
            ]
        )

    @pytest.mark.long
    def test_start_shortcuts(self):
        self.expect_command_result_contains(
            '/start skroty',
            [
                "/s", "/k", "/sz", "/l", "/w", "/o", "/d", "/kom", "/pk", "/uk",
                "/mk", "/z", "/wys", "/r", "/sub",
            ]
        )
