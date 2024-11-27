import pytest

import bot.responses.not_sending_videos.delete_clip_handler_responses as delete_msg
import bot.responses.not_sending_videos.my_clips_handler_responses as myclips_msg
import bot.responses.not_sending_videos.save_clip_handler_responses as save_msg
from bot.tests.base_test import BaseTest


class TestMyClipsCommand(BaseTest):
    @pytest.mark.quick
    def test_myclips_no_clips(self):
        self.expect_command_result_contains(
            '/mojeklipy',
            [myclips_msg.get_no_saved_clips_message()],
        )

    @pytest.mark.long
    def test_myclips_with_clips(self):
        self.send_command('/klip cytat')
        self.expect_command_result_contains(
            '/zapisz test_clip',
            [save_msg.get_clip_saved_successfully_message("test_clip")],
        )
        self.expect_command_result_contains('/mojeklipy', ["test_clip"])
        self.expect_command_result_contains(
            '/usunklip 1',
            [delete_msg.get_clip_deleted_message("test_clip")],
        )
