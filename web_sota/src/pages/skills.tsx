import { BookOpen, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { API_BASE } from "@/lib/api";

interface SkillMeta {
  name: string;
  path: string;
}

export function Skills() {
  const [skills, setSkills] = useState<SkillMeta[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [content, setContent] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/skills`)
      .then((r) => r.json())
      .then((d) => {
        setSkills(d.skills ?? []);
        setLoading(false);
      })
      .catch(() => {
        setError("Backend unreachable — cannot load skills.");
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (!selected) {
      setContent("");
      return;
    }
    fetch(`${API_BASE}/api/skills/${selected}`)
      .then((r) => r.text())
      .then(setContent)
      .catch(() => setContent("Failed to load skill content."));
  }, [selected]);

  return (
    <div className="space-y-6" data-testid="skills-page">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Skills</h2>
        <p className="text-slate-400">
          Bundled SKILL.md files — how this MCP server should be used by agents
          and clients.
        </p>
      </div>

      {loading && (
        <div
          className="flex items-center gap-2 text-slate-400"
          data-testid="skills-loading"
        >
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading skills…
        </div>
      )}

      {error && (
        <Card className="border-red-900/60 bg-red-950/30">
          <CardContent className="py-4 text-sm text-red-300">
            {error}
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <div className="space-y-2" data-testid="skills-list">
          {skills.map((s) => (
            <button
              key={s.name}
              type="button"
              onClick={() => setSelected(s.name)}
              className={`flex w-full items-center gap-2 rounded-md border px-3 py-2 text-left text-sm transition-colors ${
                selected === s.name
                  ? "border-blue-600 bg-blue-950/40 text-blue-200"
                  : "border-slate-800 bg-slate-950/50 text-slate-300 hover:bg-slate-900"
              }`}
            >
              <BookOpen className="h-4 w-4 shrink-0" />
              {s.name}
            </button>
          ))}
          {!loading && skills.length === 0 && (
            <p className="text-sm text-slate-500">
              No skills exposed by the server.
            </p>
          )}
        </div>

        <Card
          className="border-slate-800 bg-slate-950/50 md:col-span-2"
          data-testid="skills-content"
        >
          <CardHeader>
            <CardTitle className="text-sm font-medium text-slate-200">
              {selected ?? "Select a skill"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {selected ? (
              <pre className="whitespace-pre-wrap rounded-lg border border-slate-800 bg-slate-900/60 p-4 font-mono text-xs leading-relaxed text-slate-300">
                {content || "Loading…"}
              </pre>
            ) : (
              <p className="text-sm text-slate-500">
                Pick a skill from the list to read its full SKILL.md content.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
