import pytest

from bot.tests.base_test import BaseTest


class TestTranscriptionCommand(BaseTest):

    @pytest.mark.quick
    def test_transcription_existing_quote(self):
        self.expect_command_result_contains(
            '/transkrypcja Nie szkoda panu tego pięknego gabinetu?',
            ["Trudne powroty"]
        )

    @pytest.mark.quick
    def test_transcription_nonexistent_quote(self):
        self.expect_command_result_contains(
            '/transkrypcja asdfghijk',
            ["❌ Nie znaleziono pasujących cytatów dla: 'asdfghijk'.❌"]
        )
