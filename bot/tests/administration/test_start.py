import pytest
from bot.tests.base_test import BaseTest

class TestStartCommand(BaseTest):

    @pytest.mark.quick
    def test_start_base_commands(self):
        response = self.send_command('/start')
        expected_fragments = ["Podstawowe komendy"]
        self.assert_response_contains(response, expected_fragments)

    @pytest.mark.quick
    def test_start_invalid_command(self):
        response = self.send_command('/start nieistniejace_polecenie')
        expected_fragments = ["Niepoprawna komenda"]
        self.assert_response_contains(response, expected_fragments)

    @pytest.mark.long
    def test_start_search_commands(self):
        response = self.send_command('/start wyszukiwanie')
        expected_fragments = ["/klip", "/szukaj", "/lista", "/wybierz", "/odcinki", "/wytnij"]
        self.assert_response_contains(response, expected_fragments)

    @pytest.mark.long
    def test_start_edit_commands(self):
        response = self.send_command('/start edycja')
        expected_fragments = ["/dostosuj", "/kompiluj"]
        self.assert_response_contains(response, expected_fragments)

    @pytest.mark.long
    def test_start_management_commands(self):
        response = self.send_command('/start zarzadzanie')
        expected_fragments = ["/zapisz", "/mojeklipy", "/wyslij", "/polaczklipy", "/usunklip"]
        self.assert_response_contains(response, expected_fragments)

    @pytest.mark.long
    def test_start_reporting_command(self):
        response = self.send_command('/start raportowanie')
        expected_fragments = ["/report"]
        self.assert_response_contains(response, expected_fragments)

    @pytest.mark.long
    def test_start_subscription_command(self):
        response = self.send_command('/start subskrypcje')
        expected_fragments = ["/subskrypcja"]
        self.assert_response_contains(response, expected_fragments)

    @pytest.mark.long
    def test_start_all_commands(self):
        response = self.send_command('/start wszystko')
        expected_fragments = [
            "/klip", "/szukaj", "/lista", "/wybierz", "/odcinki", "/wytnij",
            "/dostosuj", "/kompiluj", "/zapisz", "/mojeklipy", "/wyslij",
            "/polaczklipy", "/usunklip", "/report", "/subskrypcja"
        ]
        self.assert_response_contains(response, expected_fragments)

    @pytest.mark.long
    def test_start_shortcuts(self):
        response = self.send_command('/start skroty')
        expected_fragments = [
            "/s", "/k", "/sz", "/l", "/w", "/o", "/d", "/kom", "/pk", "/uk",
            "/mk", "/z", "/wys", "/r", "/sub"
        ]
        self.assert_response_contains(response, expected_fragments)
