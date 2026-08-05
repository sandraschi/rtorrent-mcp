"""Prompt template registration tests."""

import pytest


def _make_mcp():
    from fastmcp import FastMCP

    from rtorrent_mcp.prompts import register_prompts

    mcp = FastMCP("test-server")
    register_prompts(mcp)
    return mcp


@pytest.mark.asyncio
async def test_seven_prompt_templates_registered():
    mcp = _make_mcp()
    prompts = await mcp.list_prompts()
    names = sorted(p.name for p in prompts)
    assert names == sorted(
        [
            "anime_search_prompt",
            "franchise_download_prompt",
            "legal_check_prompt",
            "tv_show_search_prompt",
            "ebook_search_prompt",
            "torrent_workflow_prompt",
            "system_status_prompt",
        ]
    )


@pytest.mark.asyncio
async def test_prompt_render():
    mcp = _make_mcp()
    result = await mcp.render_prompt("anime_search_prompt", {"anime_name": "Detective Conan", "resolution": "720p"})
    assert "Detective Conan" in str(result)
    assert "720p" in str(result)
