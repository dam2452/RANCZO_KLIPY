import pytest

import bot.responses.sending_videos.compile_clips_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestCompileClipsCommand(BaseTest):

    @pytest.mark.asyncio
    async def test_compile_clip_range(self):
        message = await self.send_command('/szukaj kozioł')
        await self.assert_message_hash_matches(message, expected_key="search_kozioł_results.message")

        response = await self.send_command('/kompiluj 1-4', timeout=60)
        await self.assert_command_result_file_matches(response, 'compile_kozioł_1-4.mp4')

    @pytest.mark.asyncio
    async def test_compile_specific_clips(self):
        message = await self.send_command('/szukaj kozioł')
        await self.assert_message_hash_matches(message, expected_key="search_kozioł_results.message")

        response = await self.send_command('/kompiluj 1 3 5', timeout=60)
        await self.assert_command_result_file_matches(response, 'compile_kozioł_1_3_5.mp4')

    @pytest.mark.asyncio
    async def test_compile_invalid_range(self):
        message = await self.send_command('/szukaj kozioł')
        await self.assert_message_hash_matches(message, expected_key="search_kozioł_results.message")

        response = await self.send_command('/kompiluj 5-3', timeout=60)
        self.assert_response_contains(response, [msg.get_invalid_range_message("5-3")])

    @pytest.mark.asyncio
    async def test_compile_invalid_index(self):
        message = await self.send_command('/szukaj kozioł')
        await self.assert_message_hash_matches(message, expected_key="search_kozioł_results.message")

        response = await self.send_command('/kompiluj abc', timeout=60)
        self.assert_response_contains(response, [msg.get_invalid_index_message("abc")])

    @pytest.mark.asyncio
    async def test_compile_all_clips(self):
        message = await self.send_command('/szukaj Anglii')
        await self.assert_message_hash_matches(message, expected_key="search_anglii_results.message")

        response = await self.send_command('/kompiluj wszystko', timeout=60)
        await self.assert_command_result_file_matches(response, 'compile_anglii_all.mp4')

    @pytest.mark.asyncio
    async def test_no_previous_search_results(self):
        response = await self.send_command('/kompiluj wszystko', timeout=60)
        self.assert_response_contains(response, [msg.get_no_previous_search_results_message()])

    @pytest.mark.asyncio
    async def test_no_matching_segments_found(self):
        message = await self.send_command('/szukaj brak_klipów')
        await self.assert_message_hash_matches(message, expected_key="search_no_clips_results.message")

        response = await self.send_command('/kompiluj 1-5', timeout=60)
        self.assert_response_contains(response, [msg.get_no_previous_search_results_message()])

    @pytest.mark.asyncio
    async def test_compile_exceeding_max_clips(self):
        await self.switch_to_normal_user()
        message = await self.send_command('/szukaj Anglii')
        await self.assert_message_hash_matches(message, expected_key="search_anglii_results.message")

        response = await self.send_command('/kompiluj 1-1000', timeout=60)
        self.assert_response_contains(response, [msg.get_max_clips_exceeded_message()])

    @pytest.mark.asyncio
    async def test_compile_exceeding_total_duration(self):
        await self.switch_to_normal_user()
        message = await self.send_command('/szukaj geniusz')
        await self.assert_message_hash_matches(message, expected_key="search_geniusz_results.message")

        response = await self.send_command('/kompiluj 1-25', timeout=60)
        self.assert_response_contains(response, [msg.get_clip_time_message()])
