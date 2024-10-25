import pytest

from bot.tests.base_test import BaseTest


class TestTranscriptionCommand(BaseTest):

    @pytest.mark.quick
    def test_transcription_existing_quote(self):
        response = self.send_command('/transkrypcja Nie szkoda panu tego pięknego gabinetu?')
        expected_fragments = ["📺 Trudne powroty 📺"]
        self.assert_response_contains(response, expected_fragments)

    @pytest.mark.quick
    def test_transcription_nonexistent_quote(self):
        response = self.send_command('/transkrypcja asdfghijk')
        expected_fragments = ["❌ Nie znaleziono pasujących cytatów dla: 'asdfghijk'.❌"]
        self.assert_response_contains(response, expected_fragments)
