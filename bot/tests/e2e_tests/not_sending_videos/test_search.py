from bot.tests.e2e_tests.base_test import BaseE2ETest


class TestSearchCommand(BaseE2ETest):
    def test_search(self):
        test_cases = [
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

        self.run_test_cases(test_cases)
