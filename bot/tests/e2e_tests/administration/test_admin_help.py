from bot.tests.e2e_tests.base_test import BaseE2ETest


class TestAdminCommand(BaseE2ETest):
    def test_admin(self):
        test_cases = [
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

        self.run_test_cases(test_cases)
