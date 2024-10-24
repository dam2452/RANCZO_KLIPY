from bot.tests.e2e_tests.base_test import BaseE2ETest


class TestStartCommand(BaseE2ETest):
    def test_start(self):
        test_cases = [
            {
                'command': '/start',
                'expected_fragments': [
                    "Podstawowe komendy",
                ],
            },
        ]

        self.run_test_cases(test_cases)
