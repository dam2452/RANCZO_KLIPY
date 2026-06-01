import pytest

from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool")
class TestClipSubtitlesEndpoint(BaseTest):

    @pytest.mark.asyncio
    async def test_clip_subtitles_returns_lines(self):
        response = self.client.post(
            "rest/clip-subtitles",
            json={
                "video_path": "ranczo/s01e01.mp4",
                "start_time": 0.0,
                "end_time": 300.0,
            },
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "lines" in data
        assert isinstance(data["lines"], list)

    @pytest.mark.asyncio
    async def test_clip_subtitles_line_structure(self):
        response = self.client.post(
            "rest/clip-subtitles",
            json={
                "video_path": "ranczo/s01e01.mp4",
                "start_time": 0.0,
                "end_time": 300.0,
            },
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 200
        data = response.json()
        for line in data["lines"]:
            assert "start_time" in line
            assert "end_time" in line
            assert "text" in line
            assert isinstance(line["start_time"], float)
            assert isinstance(line["end_time"], float)
            assert isinstance(line["text"], str)
            assert line["start_time"] >= 0.0
            assert line["end_time"] > line["start_time"]

    @pytest.mark.asyncio
    async def test_clip_subtitles_empty_range(self):
        response = self.client.post(
            "rest/clip-subtitles",
            json={
                "video_path": "ranczo/s01e01.mp4",
                "start_time": 9999.0,
                "end_time": 10000.0,
            },
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["lines"] == []

    @pytest.mark.asyncio
    async def test_clip_subtitles_missing_video_path(self):
        response = self.client.post(
            "rest/clip-subtitles",
            json={
                "start_time": 0.0,
                "end_time": 10.0,
            },
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_clip_subtitles_invalid_time_range(self):
        response = self.client.post(
            "rest/clip-subtitles",
            json={
                "video_path": "ranczo/s01e01.mp4",
                "start_time": -1.0,
                "end_time": 10.0,
            },
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_clip_subtitles_unauthorized(self):
        response = self.client.post(
            "rest/clip-subtitles",
            json={
                "video_path": "ranczo/s01e01.mp4",
                "start_time": 0.0,
                "end_time": 60.0,
            },
        )
        assert response.status_code in {401, 403}
