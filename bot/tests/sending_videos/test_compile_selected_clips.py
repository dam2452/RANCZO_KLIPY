import pytest

from bot.database.response_keys import ResponseKey as RK
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestCompileSelectedClipsHandler(BaseTest):

    @pytest.mark.asyncio
    async def test_merge_multiple_clips(self):
        clips = [
            {"name": "klip1", "command": "/klip geniusz", "file": "clip_geniusz_saved.mp4"},
            {"name": "klip2", "command": "/klip kozioł", "file": "clip_kozioł_saved.mp4"},
            {"name": "klip3", "command": "/klip uczniowie", "file": "clip_uczniowie_saved.mp4"},
        ]

        for clip in clips:
            response = await self.send_command(clip["command"])
            await self.assert_command_result_file_matches(response, clip["file"])
            await self.send_command(f'/zapisz {clip["name"]}')

        compile_params = "1 2 3"
        response = await self.send_command(f'/polaczklipy {compile_params}', timeout=60)
        await self.assert_command_result_file_matches(response, f'merged_clip_{compile_params}.mp4')

    @pytest.mark.asyncio
    async def test_merge_invalid_clip_numbers(self):
        response = await self.send_command('/klip geniusz')
        await self.assert_command_result_file_matches(response, 'clip_geniusz_saved.mp4')
        await self.send_command('/zapisz klip1')

        response = await self.send_command('/klip kozioł')
        await self.assert_command_result_file_matches(response, 'clip_kozioł_saved.mp4')
        await self.send_command('/zapisz klip2')

        response = await self.send_command('/polaczklipy 1 5')
        self.assert_response_contains(response, [await self.get_response(RK.INVALID_ARGS_COUNT)])

    @pytest.mark.asyncio
    async def test_merge_single_clip(self):
        response = await self.send_command('/klip geniusz')
        await self.assert_command_result_file_matches(response, 'clip_geniusz_saved.mp4')
        await self.send_command('/zapisz klip1')

        response = await self.send_command('/polaczklipy 1')
        await self.assert_command_result_file_matches(response, 'merged_single_clip_1.mp4')

    @pytest.mark.asyncio
    async def test_merge_no_clips(self):
        response = await self.send_command('/polaczklipy 1 2')
        self.assert_response_contains(response, [await self.get_response(RK.NO_MATCHING_CLIPS_FOUND)])

    @pytest.mark.asyncio
    async def test_merge_clips_with_special_characters_in_name(self):
        response = await self.send_command('/klip geniusz')
        await self.assert_command_result_file_matches(response, 'clip_geniusz_saved.mp4')
        await self.send_command('/zapisz klip@specjalny!')

        response = await self.send_command('/polaczklipy 1')
        await self.assert_command_result_file_matches(response, 'merged_special_name_clip.mp4')
