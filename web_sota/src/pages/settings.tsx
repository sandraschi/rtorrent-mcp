import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { API_BASE, getPlexStatus, scanPlex, triggerPlexIngest } from "@/lib/api";

interface ProviderInfo {
  name: string;
  port: number;
  detected: boolean;
  models: string[];
}

function LLMSettings() {
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [status, setStatus] = useState<"loading" | "ready" | "error">(
    "loading",
  );
  const [selectedProvider, setSelectedProvider] = useState("ollama");
  const [selectedModel, setSelectedModel] = useState("");

  useEffect(() => {
    let cancelled = false;
    fetch(`${API_BASE}/api/llm/discover`)
      .then((r) => r.json())
      .then((d) => {
        if (cancelled) return;
        const detected = (d.providers ?? []).filter(
          (p: ProviderInfo) => p.detected,
        );
        setProviders(d.providers ?? []);
        const savedP =
          localStorage.getItem("llm_provider") || d.default || "ollama";
        const savedM = localStorage.getItem("llm_model") || "";
        const active =
          detected.find((p: ProviderInfo) => p.name === savedP) || detected[0];
        if (active) {
          setSelectedProvider(active.name);
          const models = active.models || [];
          setSelectedModel(
            savedM && models.includes(savedM) ? savedM : models[0] || "",
          );
        }
        setStatus(detected.length > 0 ? "ready" : "error");
      })
      .catch(() => {
        if (cancelled) return;
        setProviders([]);
        setStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const active = providers.find((p) => p.name === selectedProvider);
  const models = active?.models ?? [];

  const save = (p: string, m: string) => {
    localStorage.setItem("llm_provider", p);
    localStorage.setItem("llm_model", m);
  };

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-slate-200">Local LLM</h3>
        <span
          className={`inline-flex items-center gap-1.5 text-xs ${
            status === "ready" ? "text-emerald-400" : "text-amber-400"
          }`}
          data-testid="llm-status"
        >
          <span
            className={`h-2 w-2 rounded-full ${
              status === "ready" ? "bg-emerald-400" : "bg-amber-400"
            }`}
          />
          {status === "loading"
            ? "Detecting…"
            : status === "ready"
              ? "Detected"
              : "Not detected"}
        </span>
      </div>

      {providers.length === 0 && (
        <p className="text-sm text-amber-300/90">
          Install Ollama or LM Studio to enable AI features (Ollama :11434, LM
          Studio :1234).
        </p>
      )}

      {providers.length > 0 && (
        <>
          <select
            data-testid="llm-provider-select"
            className="h-9 w-full rounded-md border border-slate-700 bg-slate-900 px-3 text-sm text-slate-200"
            value={selectedProvider}
            onChange={(e) => {
              setSelectedProvider(e.target.value);
              const next = providers.find((p) => p.name === e.target.value);
              setSelectedModel(next?.models?.[0] ?? "");
              save(e.target.value, next?.models?.[0] ?? "");
            }}
          >
            {providers.map((p) => (
              <option key={p.name} value={p.name}>
                {p.name} :{p.port}
              </option>
            ))}
          </select>

          <select
            data-testid="llm-model-select"
            className="h-9 w-full rounded-md border border-slate-700 bg-slate-900 px-3 text-sm text-slate-200"
            value={selectedModel}
            onChange={(e) => {
              setSelectedModel(e.target.value);
              save(selectedProvider, e.target.value);
            }}
          >
            {models.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </>
      )}

      <p className="text-xs text-slate-500">
        Used by AI tools. Selection persisted to browser storage (llm_provider /
        llm_model).
      </p>
    </div>
  );
}

export function Settings() {
  return (
    <div className="space-y-6" data-testid="settings-page">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">
          Configuration
        </h2>
        <p className="text-slate-400">
          Server settings live in{" "}
          <code className="text-xs text-slate-300">.env</code> and MCP config.
          The LLM section auto-detects local providers.
        </p>
      </div>

      <div className="grid gap-6">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">MCP HTTP (reference)</CardTitle>
            <CardDescription className="text-slate-400">
              Default when using{" "}
              <code className="text-xs">web_sota/start.ps1</code>
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-2">
              <Label className="text-slate-300">Streamable MCP URL</Label>
              <Input
                readOnly
                className="bg-slate-900 border-slate-800 text-slate-100"
                defaultValue="http://127.0.0.1:10910/mcp"
              />
            </div>
            <p className="text-xs text-slate-500">
              rTorrent / BitTorrent: configure{" "}
              <code className="text-xs">RTORRENT_*</code> in{" "}
              <code className="text-xs">.env</code> (see repo README).
            </p>
            <Button
              variant="outline"
              disabled
              className="border-slate-800 text-slate-500"
            >
              Not persisted from this UI
            </Button>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">Plex Ingestion & Media Integration</CardTitle>
            <CardDescription className="text-slate-400">
              Configure Plex/Jellyfin library refresh and file link modes
            </CardDescription>
          </CardHeader>
          <CardContent>
            <PlexSettings />
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">LLM Provider</CardTitle>
            <CardDescription className="text-slate-400">
              Local model endpoint configuration
            </CardDescription>
          </CardHeader>
          <CardContent>
            <LLMSettings />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function PlexSettings() {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [actionMsg, setActionMsg] = useState<string | null>(null);

  useEffect(() => {
    getPlexStatus().then(setStatus).catch(() => setStatus(null));
  }, []);

  async function handleScan() {
    setLoading(true);
    setActionMsg(null);
    try {
      const res = await scanPlex();
      if (res.success) {
        setActionMsg("Plex library refresh scan triggered successfully.");
      } else {
        setActionMsg(`Plex scan error: ${res.error || "Failed"}`);
      }
    } catch (e) {
      setActionMsg(`Scan exception: ${e instanceof Error ? e.message : "Error"}`);
    } finally {
      setLoading(false);
    }
  }

  async function handleIngest() {
    setLoading(true);
    setActionMsg(null);
    try {
      const res = await triggerPlexIngest();
      if (res.success) {
        setActionMsg(`Ingestion pass complete. Processed ${res.completed_found ?? 0} downloads.`);
      } else {
        setActionMsg(`Ingest error: ${res.error || "Failed"}`);
      }
    } catch (e) {
      setActionMsg(`Ingest exception: ${e instanceof Error ? e.message : "Error"}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-3 text-sm">
        <div className="flex items-center justify-between rounded-md border border-slate-800 bg-slate-900 p-3">
          <span className="text-slate-400">Plex URL Configured:</span>
          <span className={`font-mono text-xs font-semibold ${status?.configured ? "text-green-400" : "text-amber-400"}`}>
            {status?.configured ? (status?.plex_url || "Configured") : "Not configured (.env PLEX_URL)"}
          </span>
        </div>
        <div className="flex items-center justify-between rounded-md border border-slate-800 bg-slate-900 p-3">
          <span className="text-slate-400">Link Mode (Seeding Preservation):</span>
          <span className="font-mono text-xs font-semibold text-blue-300">
            {status?.link_mode || "hardlink (Default)"}
          </span>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3 pt-2">
        <Button
          onClick={handleScan}
          disabled={loading || !status?.configured}
          variant="outline"
          className="border-slate-800 bg-slate-900 text-slate-100 hover:bg-slate-800"
        >
          {loading ? "Triggering..." : "Scan Plex Libraries Now"}
        </Button>
        <Button
          onClick={handleIngest}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-500 text-white"
        >
          {loading ? "Processing..." : "Run Post-Processing Ingest Pass"}
        </Button>
      </div>

      {actionMsg && (
        <p className="text-xs font-mono text-slate-300 bg-slate-900 p-2.5 rounded border border-slate-800">
          {actionMsg}
        </p>
      )}
    </div>
  );
}
