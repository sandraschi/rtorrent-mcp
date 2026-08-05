"""Transport config tests (pure functions in transport.py)."""

from rtorrent_mcp.transport import get_transport_config, resolve_config, resolve_transport


class _Args:
    def __init__(self, **kw):
        self.http = kw.get("http", False)
        self.sse = kw.get("sse", False)
        self.stdio = kw.get("stdio", False)
        self.host = kw.get("host")
        self.port = kw.get("port")
        self.path = kw.get("path")
        self.debug = False


def test_default_transport_config(monkeypatch):
    monkeypatch.delenv("MCP_TRANSPORT", raising=False)
    monkeypatch.delenv("MCP_PORT", raising=False)
    monkeypatch.delenv("MCP_HOST", raising=False)
    monkeypatch.delenv("MCP_PATH", raising=False)
    cfg = get_transport_config()
    assert cfg["transport"] == "stdio"
    assert cfg["port"] == 10910
    assert cfg["host"] == "127.0.0.1"
    assert cfg["path"] == "/mcp"


def test_env_transport_config(monkeypatch):
    monkeypatch.setenv("MCP_TRANSPORT", "http")
    monkeypatch.setenv("MCP_PORT", "10999")
    monkeypatch.setenv("MCP_HOST", "10.0.0.5")
    monkeypatch.setenv("MCP_PATH", "/rpc")
    cfg = get_transport_config()
    assert cfg["transport"] == "http"
    assert cfg["port"] == 10999
    assert cfg["host"] == "10.0.0.5"
    assert cfg["path"] == "/rpc"


def test_invalid_port_falls_back(monkeypatch):
    monkeypatch.setenv("MCP_PORT", "not-a-number")
    cfg = get_transport_config()
    assert cfg["port"] == 10910


def test_resolve_transport_cli_wins(monkeypatch):
    monkeypatch.setenv("MCP_TRANSPORT", "stdio")
    assert resolve_transport(_Args(http=True)) == "http"
    assert resolve_transport(_Args(stdio=True)) == "stdio"
    assert resolve_transport(_Args(sse=True)) == "sse"


def test_resolve_transport_env_fallback(monkeypatch):
    monkeypatch.setenv("MCP_TRANSPORT", "http")
    assert resolve_transport(_Args()) == "http"
    monkeypatch.setenv("MCP_TRANSPORT", "bogus")
    assert resolve_transport(_Args()) == "stdio"


def test_resolve_config_precedence(monkeypatch):
    monkeypatch.setenv("MCP_PORT", "10910")
    monkeypatch.setenv("MCP_HOST", "127.0.0.1")
    cfg = resolve_config(_Args(http=True, port=10977, host="10.0.0.5"))
    assert cfg["transport"] == "http"
    assert cfg["port"] == 10977
    assert cfg["host"] == "10.0.0.5"

    cfg2 = resolve_config(_Args(http=True, host="127.0.0.1"))
    assert cfg2["port"] == 10910
