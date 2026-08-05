"""Sampling handler tests (openai_sampling_handler.py)."""

from unittest.mock import MagicMock

import pytest
from mcp.types import CreateMessageRequestParams as SamplingParams
from mcp.types import CreateMessageResult, SamplingMessage, TextContent


def _make_settings(**overrides):
    from rtorrent_mcp.config.settings import Settings

    defaults = {
        "RTORRENT_SAMPLING_BASE_URL": "http://127.0.0.1:11434/v1",
        "RTORRENT_SAMPLING_API_KEY": None,
        "RTORRENT_SAMPLING_MODEL": "llama3.2",
    }
    defaults.update(overrides)
    return Settings(**defaults)


def _handler(config=None):
    from rtorrent_mcp.sampling.openai_sampling_handler import RTorrentSamplingHandler

    return RTorrentSamplingHandler(config=config)


def _msg(text="hello"):
    return SamplingMessage(role="user", content=TextContent(type="text", text=text))


def _params(max_tokens=200, temperature=0.7):
    return SamplingParams(messages=[_msg()], maxTokens=max_tokens, temperature=temperature)


class TestModuleHelpers:
    def test_hint_model_uses_preferences(self):
        from mcp.types import ModelHint, ModelPreferences

        from rtorrent_mcp.sampling.openai_sampling_handler import _hint_model

        prefs = ModelPreferences(hints=[ModelHint(name="qwen3:8b")])
        assert _hint_model(_params(), "llama3.2") == "llama3.2"
        params = _params()
        params.modelPreferences = prefs
        assert _hint_model(params, "llama3.2") == "qwen3:8b"

    def test_tool_choice_openai(self):
        from mcp.types import ToolChoice

        from rtorrent_mcp.sampling.openai_sampling_handler import _tool_choice_openai

        assert _tool_choice_openai(None) == "auto"
        assert _tool_choice_openai(ToolChoice(mode="required")) == "required"
        assert _tool_choice_openai(ToolChoice(mode="none")) == "none"
        assert _tool_choice_openai(ToolChoice(mode="auto")) == "auto"

    def test_mcp_tools_to_openai(self):
        from mcp.types import Tool

        from rtorrent_mcp.sampling.openai_sampling_handler import _mcp_tools_to_openai

        assert _mcp_tools_to_openai(None) is None
        tool = Tool(name="test_tool", description="A test tool", inputSchema={"type": "object"})
        out = _mcp_tools_to_openai([tool])
        assert out[0]["function"]["name"] == "test_tool"
        assert out[0]["function"]["parameters"] == {"type": "object"}

    def test_sampling_http_enabled(self):
        from rtorrent_mcp.sampling.openai_sampling_handler import _sampling_http_enabled

        assert _sampling_http_enabled(None, "http://127.0.0.1:11434/v1") is True
        assert _sampling_http_enabled(None, "https://api.openai.com/v1") is False
        assert _sampling_http_enabled("sk-123", "https://api.openai.com/v1") is True
        assert _sampling_http_enabled(None, "") is False


class TestHealthAndModels:
    @pytest.mark.asyncio
    async def test_check_health_configured(self):
        h = _handler(_make_settings())
        result = await h.check_health()
        assert result["status"] == "healthy"
        assert result["server_side_llm_configured"] is True
        assert result["sampling_base_url"] == "http://127.0.0.1:11434/v1"
        assert result["sampling_fallback_model"] == "llama3.2"

    @pytest.mark.asyncio
    async def test_check_health_unconfigured(self):
        h = _handler(_make_settings(RTORRENT_SAMPLING_BASE_URL=""))
        result = await h.check_health()
        assert result["server_side_llm_configured"] is False

    def test_available_models(self):
        h = _handler(_make_settings())
        assert h.get_available_models() == ["llama3.2"]
        h2 = _handler(_make_settings(RTORRENT_SAMPLING_BASE_URL=""))
        assert h2.get_available_models() == []


class TestCall:
    @pytest.mark.asyncio
    async def test_degraded_without_endpoint(self):
        h = _handler(_make_settings(RTORRENT_SAMPLING_BASE_URL=""))
        result = await h([_msg()], _params(), None)
        assert isinstance(result, CreateMessageResult)
        assert "sampling" in result.content.text.lower() or "not configured" in result.content.text.lower()

    @pytest.mark.asyncio
    async def test_success_returns_text(self, monkeypatch):
        import httpx

        class FakeResponse:
            status_code = 200

            def raise_for_status(self):
                return None

            def json(self):
                return {"choices": [{"message": {"content": "Ollama says hi"}}]}

        class FakeClient:
            def __init__(self, *a, **k):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *a):
                return False

            async def post(self, *a, **k):
                return FakeResponse()

        monkeypatch.setattr(httpx, "AsyncClient", FakeClient)
        h = _handler(_make_settings())
        result = await h([_msg("what is 2+2?")], _params(), None)
        assert isinstance(result, CreateMessageResult)
        assert result.content.text == "Ollama says hi"
        assert result.role == "assistant"

    @pytest.mark.asyncio
    async def test_http_error_returns_message(self, monkeypatch):
        import httpx

        class FakeResponse:
            status_code = 503
            text = "model not found"

        class FakeClient:
            def __init__(self, *a, **k):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *a):
                return False

            async def post(self, *a, **k):
                resp = FakeResponse()
                raise httpx.HTTPStatusError("503", request=MagicMock(), response=resp)

        monkeypatch.setattr(httpx, "AsyncClient", FakeClient)
        h = _handler(_make_settings())
        result = await h([_msg()], _params(), None)
        assert isinstance(result, CreateMessageResult)
        assert "HTTP 503" in result.content.text

    @pytest.mark.asyncio
    async def test_network_error_returns_message(self, monkeypatch):
        import httpx

        class FakeClient:
            def __init__(self, *a, **k):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *a):
                return False

            async def post(self, *a, **k):
                raise httpx.ConnectError("refused")

        monkeypatch.setattr(httpx, "AsyncClient", FakeClient)
        h = _handler(_make_settings())
        result = await h([_msg()], _params(), None)
        assert isinstance(result, CreateMessageResult)
        assert "Request failed" in result.content.text
