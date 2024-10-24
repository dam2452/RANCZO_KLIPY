import pytest
from bot.tests.e2e_tests.base_test import BaseE2ETest


class TestAdminCommand(BaseE2ETest):
    quick_test_cases = [
        {
            'command': ['/admin'],
            'expected_fragments': [
                "/addwhitelist",
                "/removewhitelist",
                "/listwhitelist",
                "/listadmins",
                "/listmoderators",
                "/klucz",
                "/listkey",
                "/addkey",
                "/removekey",
                "/addsubscription",
                "/removesubscription",
                "/transkrypcja"
            ],
        },
    ]

    long_test_cases = quick_test_cases + [
        {
            'command': ['/admin skroty'],
            'expected_fragments': [
                "/addw",
                "/rmw",
                "/lw",
                "/la",
                "/lm",
                "/klucz",
                "/lk",
                "/addk",
                "/rmk",
                "/addsub",
                "/rmsub",
                "/t"
            ],
        },
        {
            'command': ['/admin nieistniejace_polecenie'],
            'expected_fragments': [
                "/addwhitelist",
                "/removewhitelist",
                "/listwhitelist",
                "/listadmins",
                "/listmoderators",
                "/klucz",
                "/listkey",
                "/addkey",
                "/removekey",
                "/addsubscription",
                "/removesubscription",
                "/transkrypcja"
            ],
        },
    ]

    @pytest.mark.long
    def test_admin_long(self):
        self.run_test_cases(self.long_test_cases)

    @pytest.mark.quick
    def test_admin_quick(self):
        self.run_test_cases(self.quick_test_cases)
