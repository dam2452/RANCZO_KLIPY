import pytest

from bot.tests.base_test import BaseTest


class TestAdminCommand(BaseTest):

    @pytest.mark.quick
    def test_admin_base_command(self):
        self.expect_command_result_contains(
            '/admin',
            [
                "/addwhitelist", "/removewhitelist", "/listwhitelist", "/listadmins",
                "/listmoderators", "/klucz", "/listkey", "/addkey", "/removekey",
                "/addsubscription", "/removesubscription", "/transkrypcja",
            ]
        )

    @pytest.mark.long
    def test_admin_shortcuts(self):
        self.expect_command_result_contains(
            '/admin skroty',
            [
                "/addw", "/rmw", "/lw", "/la", "/lm", "/klucz", "/lk",
                "/addk", "/rmk", "/addsub", "/rmsub", "/t",
            ]
        )

    @pytest.mark.long
    def test_admin_invalid_command(self):
        self.expect_command_result_contains(
            '/admin nieistniejace_polecenie',
            [
                "/addwhitelist", "/removewhitelist", "/listwhitelist", "/listadmins",
                "/listmoderators", "/klucz", "/listkey", "/addkey", "/removekey",
                "/addsubscription", "/removesubscription", "/transkrypcja",
            ]
        )
