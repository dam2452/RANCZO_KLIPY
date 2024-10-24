import pytest

from bot.tests.e2e_tests.base_test import BaseE2ETest


class TestStartCommand(BaseE2ETest):
    @pytest.mark.long
    def test_start_long(self):
        test_cases = [
            {
                'command': ['/start'],
                'expected_fragments': [
                    "Podstawowe komendy",
                ],
            },
            {
                'command': ['/start wyszukiwanie'],
                'expected_fragments': [
                    "/klip",
                    "/szukaj",
                    "/lista",
                    "/wybierz",
                    "/odcinki",
                    "/wytnij",
                ],
            },
            {
                'command': ['/start edycja'],
                'expected_fragments': [
                    "/dostosuj",
                    "/kompiluj",
                ],
            },
            {
                'command': ['/start zarzadzanie'],
                'expected_fragments': [
                    "/zapisz",
                    "/mojeklipy",
                    "/wyslij",
                    "/polaczklipy",
                    "/usunklip",
                ],
            },
            {
                'command': ['/start raportowanie'],
                'expected_fragments': [
                    "/report",
                ],
            },
            {
                'command': ['/start subskrypcje'],
                'expected_fragments': [
                    "/subskrypcja",
                ],
            },
            {
                'command': ['/start wszystko'],
                'expected_fragments': [
                    "/klip",
                    "/szukaj",
                    "/lista",
                    "/wybierz",
                    "/odcinki",
                    "/wytnij",
                    "/dostosuj",
                    "/kompiluj",
                    "/zapisz",
                    "/mojeklipy",
                    "/wyslij",
                    "/polaczklipy",
                    "/usunklip",
                    "/report",
                    "/subskrypcja",
                ],
            },
            {
                'command': ['/start skroty'],
                'expected_fragments': [
                    "/s",
                    "/k",
                    "/sz",
                    "/l",
                    "/w",
                    "/o",
                    "/d",
                    "/kom",
                    "/pk",
                    "/uk",
                    "/mk",
                    "/z",
                    "/wys",
                    "/r",
                    "/sub",
                ],
            },
        ]

        self.run_test_cases(test_cases)

    @pytest.mark.quick
    def test_start_quick(self):
        test_cases = [
            {
                'command': ['/start'],
                'expected_fragments': [
                    "Podstawowe komendy",
                ],
            },
        ]

        self.run_test_cases(test_cases)
