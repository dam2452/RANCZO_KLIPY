import pytest

from bot.tests.base_test import BaseTest


class TestAdminCommand(BaseTest):

    @pytest.mark.quick
    def test_admin_base_command(self):
        response = self.send_command('/admin')
        expected_fragments = [
            "/addwhitelist", "/removewhitelist", "/listwhitelist", "/listadmins",
            "/listmoderators", "/klucz", "/listkey", "/addkey", "/removekey",
            "/addsubscription", "/removesubscription", "/transkrypcja",
        ]
        self.assert_response_contains(response, expected_fragments)

    @pytest.mark.long
    def test_admin_shortcuts(self):
        response = self.send_command('/admin skroty')
        expected_fragments = [
            "/addw", "/rmw", "/lw", "/la", "/lm", "/klucz", "/lk",
            "/addk", "/rmk", "/addsub", "/rmsub", "/t",
        ]
        self.assert_response_contains(response, expected_fragments)

    @pytest.mark.long
    def test_admin_invalid_command(self):
        response = self.send_command('/admin nieistniejace_polecenie')
        expected_fragments = [
            "/addwhitelist", "/removewhitelist", "/listwhitelist", "/listadmins",
            "/listmoderators", "/klucz", "/listkey", "/addkey", "/removekey",
            "/addsubscription", "/removesubscription", "/transkrypcja",
        ]
        self.assert_response_contains(response, expected_fragments)
