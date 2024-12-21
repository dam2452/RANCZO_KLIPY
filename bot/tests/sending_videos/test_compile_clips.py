import pytest

import bot.responses.sending_videos.compile_clips_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestCompileClipsCommand(BaseTest):

    @pytest.mark.asyncio
    async def test_compile_all_clips(self):
        message = await self.send_command('/szukaj Anglii')
        await self.assert_message_hash_matches(message, expected_key="search_anglii_results.message")

        response = await self.send_command('/kompiluj wszystko', timeout=30)
        await self.assert_command_result_file_matches(response, 'compile_anglii_all.mp4')

    @pytest.mark.asyncio
    async def test_compile_clip_range(self):
        message = await self.send_command('/szukaj kozioł')
        await self.assert_message_hash_matches(message, expected_key="search_kozioł_results.message")

        response = await self.send_command('/kompiluj 1-4')
        await self.assert_command_result_file_matches(response, 'compile_kozioł_1-4.mp4')

    @pytest.mark.asyncio
    async def test_compile_specific_clips(self):
        message = await self.send_command('/szukaj kozioł')
        await self.assert_message_hash_matches(message, expected_key="search_kozioł_results.message")

        response = await self.send_command('/kompiluj 1 3 5')
        await self.assert_command_result_file_matches(response, 'compile_kozioł_1_3_5.mp4')

    # @pytest.mark.asyncio
    # async def test_compile_invalid_range(self):
    #     message = await self.send_command('/szukaj kozioł')
    #     await self.assert_message_hash_matches(message, expected_key="szukaj_kozioł_wyniki.message")
    #
    #     response = await self.send_command('/kompiluj 5-3')
    #     self.assert_response_contains(response, [msg.get_invalid_range_message("5-3")])

    # @pytest.mark.asyncio
    # async def test_compile_invalid_index(self):
    #     message = await self.send_command('/szukaj kozioł')
    #     await self.assert_message_hash_matches(message, expected_key="szukaj_kozioł_wyniki.message")
    #
    #     response = await self.send_command('/kompiluj abc')
    #     self.assert_response_contains(response, [msg.get_invalid_index_message("abc")])

    @pytest.mark.asyncio
    async def test_no_previous_search_results(self):
        response = await self.send_command('/kompiluj wszystko', timeout=30)
        self.assert_response_contains(response, [msg.get_no_previous_search_results_message()])

    @pytest.mark.asyncio
    async def test_no_matching_segments_found(self):
        message = await self.send_command('/szukaj brak_klipów')
        await self.assert_message_hash_matches(message, expected_key="search_no_clips_results.message")

        response = await self.send_command('/kompiluj 1-5')
        self.assert_response_contains(response, [msg.get_no_previous_search_results_message()])

    # @pytest.mark.asyncio
    # async def test_compile_exceeding_max_clips(self):
    #     message = await self.send_command('/szukaj Anglii')
    #     await self.assert_message_hash_matches(message, expected_key="szukaj_Anglii_wyniki.message")
    #
    #     response = await self.send_command('/kompiluj 1-1000')
    #     self.assert_response_contains(response, [msg.get_max_clips_exceeded_message()])

    # @pytest.mark.asyncio
    # async def test_compile_exceeding_total_duration(self):
    #     message = await self.send_command('/szukaj Anglii')
    #     await self.assert_message_hash_matches(message, expected_key="szukaj_Anglii_wyniki.message")
    #
    #     response = await self.send_command('/kompiluj 1-100')
    #     self.assert_response_contains(response, [msg.get_clip_time_message()])
