"""
test_filename_normalizer.py - Unit tests for FilenameNormalizer service.
"""

from rtorrent_mcp.services.filename_normalizer import FilenameNormalizer


class TestFilenameNormalizer:
    def test_clean_anime_filename(self):
        filename = "[SubsPlease] Boku no Hero Academia - 139 (1080p) [C5819381].mkv"
        res = FilenameNormalizer.normalize(filename, category="anime")

        assert res["title"] == "Boku no Hero Academia"
        assert res["formatted_episode"] == "S01E139"
        assert res["normalized_filename"] == "Boku no Hero Academia - S01E139.mkv"
        assert res["relative_plex_path"] == "Anime/Boku no Hero Academia/Season 01/Boku no Hero Academia - S01E139.mkv"

    def test_clean_tv_filename(self):
        filename = "South.Park.S28E03.1080p.WEB-DL.AAC2.0.H.264-MeGusta.mkv"
        res = FilenameNormalizer.normalize(filename, category="tv")

        assert res["title"] == "South Park"
        assert res["season"] == 28
        assert res["episode"] == 3
        assert res["formatted_episode"] == "S28E03"
        assert res["normalized_filename"] == "South Park - S28E03.mkv"
        assert res["relative_plex_path"] == "TV Shows/South Park/Season 28/South Park - S28E03.mkv"

    def test_clean_movie_filename(self):
        filename = "The.Matrix.1999.1080p.BluRay.x264-RARBG.mp4"
        res = FilenameNormalizer.normalize(filename, category="movies")

        assert res["title"] == "The Matrix"
        assert res["year"] == 1999
        assert res["normalized_filename"] == "The Matrix (1999).mp4"
        assert res["relative_plex_path"] == "Movies/The Matrix (1999)/The Matrix (1999).mp4"

    def test_extract_season_episode_formats(self):
        res1 = FilenameNormalizer.extract_season_episode("Show.Name.S02E05.mkv")
        assert res1 == {"season": 2, "episode": 5, "formatted": "S02E05"}

        res2 = FilenameNormalizer.extract_season_episode("Show.Name.2x12.mkv")
        assert res2 == {"season": 2, "episode": 12, "formatted": "S02E12"}

        res3 = FilenameNormalizer.extract_season_episode("Anime Title - 12.mkv")
        assert res3 == {"season": 1, "episode": 12, "formatted": "S01E12"}
