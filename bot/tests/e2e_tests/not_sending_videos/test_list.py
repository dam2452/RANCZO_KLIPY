from bot.tests.e2e_tests.base_test import BaseE2ETest


class TestListCommand(BaseE2ETest):
    def test_list_after_search(self):
        response_search = self.send_command('/szukaj krowa')
        expected_text = "Znaleziono"
        assert expected_text in response_search.text, f'Oczekiwany tekst "{expected_text}" nie został znaleziony w odpowiedzi "{response_search.text}".'

        response_list = self.send_command('/lista')
        self.assert_file_matches(response_list, 'expected_list.txt', '.txt')
