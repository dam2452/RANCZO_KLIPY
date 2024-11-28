import pytest

import bot.responses.not_sending_videos.transcription_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestTranscriptionCommand(BaseTest):

    @pytest.mark.quick
    def test_transcription_existing_quote(self):
        self.expect_command_result_contains(
            '/transkrypcja Nie szkoda panu tego pięknego gabinetu?',
            ["Trudne powroty"],
        )

    @pytest.mark.quick
    def test_transcription_nonexistent_quote(self):
        self.expect_command_result_contains(
            '/transkrypcja asdfghijk',
            [msg.get_no_quote_provided_message()],
        )
