import pytest

from bot.tests.base_test import BaseTest


class TestStartCommand(BaseTest):
    quick_test_cases = [
        {
            'command': ['/start'],
            'expected_fragments': [
                "Podstawowe komendy",
            ],
        },
        {
            'command': ['/start nieistniejace_polecenie'],
            'expected_fragments': [
                "Niepoprawna komenda",
            ],
        },
    ]

    long_test_cases = quick_test_cases + [
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

    @pytest.mark.quick
    def test_start_quick(self):
        self.run_test_cases(self.quick_test_cases)

    @pytest.mark.long
    def test_start_long(self):
        self.run_test_cases(self.quick_test_cases + self.long_test_cases)
