import pytest

from bot.tests.base_test import BaseTest


class TestReportCommand(BaseTest):

    @pytest.mark.quick
    def test_report_with_valid_message(self):
        report_response = self.send_command('/report To i to nie działa')
        expected_fragments = ["✅ Dziękujemy za zgłoszenie.✅"]
        self.assert_response_contains(report_response, expected_fragments)

    @pytest.mark.quick
    def test_report_with_empty_message(self):
        report_response = self.send_command('/report')
        expected_fragments = ["❌ Podaj treść raportu.❌"]
        self.assert_response_contains(report_response, expected_fragments)

    @pytest.mark.long
    def test_report_with_special_characters_in_message(self):
        report_response = self.send_command('/report To się nie działa @#$%^&*()!')
        expected_fragments = ["✅ Dziękujemy za zgłoszenie.✅"]
        self.assert_response_contains(report_response, expected_fragments)

    @pytest.mark.long
    def test_report_with_long_message(self):
        long_message = "To i to nie działa. " * 20
        report_response = self.send_command(f'/report {long_message}')
        expected_fragments = ["✅ Dziękujemy za zgłoszenie.✅"]
        self.assert_response_contains(report_response, expected_fragments)
