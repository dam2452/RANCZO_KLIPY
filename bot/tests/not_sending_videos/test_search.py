import pytest

from bot.tests.base_test import BaseTest


class TestSearchCommand(BaseTest):
    quick_test_cases = [
        {
            'command': '/szukaj krowa',
            'expected_fragments': [
                "Znaleziono",
            ],
        },
        {
            'command': '/szukaj nieistniejące_słowo',
            'expected_fragments': [
                "❌ Nie znaleziono pasujących cytatów dla: 'nieistniejące_słowo'.❌",
            ],
        },
    ]

    @pytest.mark.quick
    def test_search_quick(self):
        self.run_test_cases(self.quick_test_cases)

    @pytest.mark.long
    def test_search_long(self):
        additional_long_test_cases = [
            {
                'command': '/sz krowa',
                'expected_fragments': [
                    "Znaleziono",
                ],
            },
            {
                'command': '/sz nieistniejące_słowo',
                'expected_fragments': [
                    "❌ Nie znaleziono pasujących cytatów dla: 'nieistniejące_słowo'.❌",
                ],
            },
        ]

        combined_test_cases = self.quick_test_cases + additional_long_test_cases

        self.run_test_cases(combined_test_cases)
