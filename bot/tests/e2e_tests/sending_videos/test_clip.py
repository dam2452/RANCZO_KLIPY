import logging
import os

from bot.tests.e2e_tests.base_e2e_test import BaseE2ETest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestClipHandler(BaseE2ETest):
    @classmethod
    def setup_class(cls):
        super().setup_class()

    @classmethod
    def teardown_class(cls):
        super().teardown_class()

    def test_clip_geniusz(self):
        response = self.send_command('/klip geniusz')

        assert response.media is not None, 'Bot nie zwrócił wideo.'

        received_video_path = self.client.download_media(response, file='received_geniusz.mp4')

        expected_video_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '..',
                'expected_videos',
                'geniusz.mp4',
            ),
        )

        assert os.path.exists(expected_video_path), f'Oczekiwane wideo {expected_video_path} nie istnieje.'

        expected_hash = self.compute_file_hash(expected_video_path)
        received_hash = self.compute_file_hash(received_video_path)

        assert expected_hash == received_hash, 'Otrzymane wideo różni się od oczekiwanego.'

        # noinspection PyTypeChecker
        os.remove(received_video_path)
