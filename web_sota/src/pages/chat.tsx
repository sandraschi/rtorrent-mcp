import {
  Bot,
  Download,
  Loader2,
  Send,
  Sparkles,
  Trash2,
  User,
} from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

const STORAGE_KEY = "qbt-mcp-chat-history";

const PERSONALITIES: Record<string, string> = {
  "Download Manager":
    "You are an expert torrent download manager. Help users find, add, and organize torrents. Advise on tracker settings, download paths, and RSS feeds for automated downloading.",
  Seeder:
    "You are a seeding specialist focused on ratio management and long-term torrent health. Advise on seeding goals, ratio groups, and disk space management for efficient sharing.",
  "Quick Summarizer":
    "You are a concise assistant. Answer in 1-3 sentences. Be direct and to the point.",
  Custom: "",
};

const EXAMPLE_PROMPTS = [
  {
    group: "Torrents",
    items: [
      "Add a new torrent from magnet link",
      "List all active downloads with ETA",
      "Prioritize a specific torrent in the queue",
    ],
  },
  {
    group: "Queue",
    items: [
      "Set maximum active downloads to 5",
      "Configure schedule for overnight downloading",
      "Pause all torrents and resume in the morning",
    ],
  },
  {
    group: "Settings",
    items: [
      "Change default download directory",
      "Set up RSS feed auto-downloading",
      "Configure speed limits for peak hours",
    ],
  },
];

function saveMessages(msgs: Message[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(msgs));
  } catch {}
}

function loadMessages(): Message[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {}
  return [];
}

export function Chat() {
  const [messages, setMessages] = useState<Message[]>(() => {
    const saved = loadMessages();
    if (saved.length > 0) return saved;
    return [
      {
        role: "assistant",
        content:
          "I'm your torrent management assistant. I can help with downloads, queuing, seeding, and qBittorrent configuration. How can I help?",
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      },
    ];
  });
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [personality, setPersonality] = useState("Download Manager");
  const [showExamples, setShowExamples] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (messages.length > 0) {
      endRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleSend = useCallback(async () => {
    const text = inputValue.trim();
    if (!text || isLoading) return;
    setShowExamples(false);

    const userMsg: Message = {
      role: "user",
      content: text,
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    const updated = [...messages, userMsg];
    setMessages(updated);
    saveMessages(updated);
    setInputValue("");
    setIsLoading(true);

    try {
      const history = updated.map((m) => ({
        role: m.role,
        content: m.content,
      }));
      const systemPrompt = PERSONALITIES[personality] || "";
      const response = await fetch("/api/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          system_prompt: systemPrompt,
          context: { history },
        }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data = await response.json();
      const reply = data.reply || data.response || "No response from model.";

      const assistantMsg: Message = {
        role: "assistant",
        content: reply,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };
      const withReply = [...updated, assistantMsg];
      setMessages(withReply);
      saveMessages(withReply);
    } catch {
      const errMsg: Message = {
        role: "assistant",
        content:
          "Request failed. Check that the backend is running and an LLM provider is configured.",
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };
      const withError = [...updated, errMsg];
      setMessages(withError);
      saveMessages(withError);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  }, [messages, isLoading, personality, inputValue]);

  const handleClear = () => {
    const fresh: Message[] = [
      {
        role: "assistant",
        content: "Conversation cleared. How can I help with your torrents?",
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      },
    ];
    setMessages(fresh);
    saveMessages(fresh);
  };

  const handleExport = () => {
    const text = messages
      .map(
        (m) =>
          `[${m.timestamp}] ${m.role === "user" ? "You" : "Assistant"}: ${m.content}`,
      )
      .join("\n\n");
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `qbt-mcp-chat-${new Date().toISOString().split("T")[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div
      className="flex flex-col space-y-4 animate-in fade-in duration-500 h-full"
      data-testid="chat-page"
    >
      <div
        className="flex items-center justify-between shrink-0"
        data-testid="chat-controls"
      >
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            <h2 className="text-2xl font-bold tracking-tight text-foreground">
              Chat
            </h2>
          </div>
          <span className="text-xs text-muted-foreground bg-muted/30 px-2 py-0.5 rounded font-mono">
            skill:torrent-manager
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span
            className="w-2 h-2 rounded-full bg-green-500 animate-pulse"
            data-testid="backend-dot"
          />
          <button
            type="button"
            onClick={handleExport}
            data-testid="chat-export"
            className="flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-xs text-muted-foreground hover:bg-secondary transition-colors"
          >
            <Download className="h-3.5 w-3.5" /> Export
          </button>
          <button
            type="button"
            onClick={handleClear}
            data-testid="chat-clear"
            className="flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-xs text-muted-foreground hover:bg-secondary transition-colors"
          >
            <Trash2 className="h-3.5 w-3.5" /> Clear
          </button>
        </div>
      </div>

      <div
        className="flex items-center gap-2 flex-wrap shrink-0"
        data-testid="personality-select"
      >
        <span className="text-xs text-muted-foreground">Personality:</span>
        {Object.keys(PERSONALITIES).map((p) => (
          <button
            key={p}
            type="button"
            onClick={() => setPersonality(p)}
            className={`px-2.5 py-1 rounded text-[10px] font-medium transition-all ${
              personality === p
                ? "bg-primary/20 text-primary border border-primary/30"
                : "bg-muted/30 text-muted-foreground border border-border/40 hover:bg-muted/50"
            }`}
          >
            {p}
          </button>
        ))}
      </div>

      <div className="flex-1 flex flex-col overflow-hidden rounded-xl border border-border bg-background/20">
        <div
          className="flex-1 overflow-y-auto p-4 space-y-4"
          data-testid="chat-messages"
        >
          {messages.map((msg, i) => (
            <div
              key={msg.timestamp ?? `${msg.role}-${i}`}
              className="flex gap-3 animate-in slide-in-from-bottom-2 duration-300"
            >
              <div
                className={`h-8 w-8 rounded-full flex items-center justify-center border shrink-0 ${
                  msg.role === "user"
                    ? "bg-secondary border-border/50"
                    : "bg-primary/10 border-primary/20"
                }`}
              >
                {msg.role === "user" ? (
                  <User className="h-4 w-4 text-primary/70" />
                ) : (
                  <Bot className="h-4 w-4 text-primary" />
                )}
              </div>
              <div className="flex-1 space-y-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span
                    className={`text-xs font-medium ${msg.role === "user" ? "text-foreground" : "text-primary"}`}
                  >
                    {msg.role === "user" ? "You" : personality}
                  </span>
                  <span className="text-[10px] text-muted-foreground">
                    {msg.timestamp}
                  </span>
                </div>
                <div
                  className={`text-sm p-3 rounded-lg border inline-block max-w-[85%] whitespace-pre-wrap ${
                    msg.role === "user"
                      ? "bg-secondary/30 border-border/30 text-foreground"
                      : "bg-primary/5 border-primary/10 text-foreground"
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-3 animate-pulse">
              <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center border border-primary/20 shrink-0">
                <Loader2 className="h-4 w-4 text-primary animate-spin" />
              </div>
              <div className="bg-primary/5 border border-primary/10 p-3 rounded-lg h-10 w-48">
                <div className="h-2 w-full bg-primary/20 rounded animate-pulse" />
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        <div className="p-4 border-t border-border/30 bg-secondary/10 shrink-0">
          {!showExamples && (
            <div
              className="mb-2 flex items-center gap-1.5 flex-wrap"
              data-testid="example-prompts"
            >
              {EXAMPLE_PROMPTS.map((group) => (
                <div key={group.group} className="flex items-center gap-1">
                  <span className="text-[10px] text-muted-foreground mr-1">
                    {group.group}:
                  </span>
                  {group.items.map((p) => (
                    <button
                      key={p}
                      type="button"
                      onClick={() => {
                        setInputValue(p);
                        inputRef.current?.focus();
                      }}
                      className="px-2 py-0.5 rounded text-[10px] bg-muted/30 text-muted-foreground hover:bg-muted/50 transition-colors border border-border/30"
                    >
                      {p}
                    </button>
                  ))}
                </div>
              ))}
              <button
                type="button"
                onClick={() => setShowExamples(true)}
                className="px-2 py-0.5 rounded text-[10px] text-primary hover:text-primary/80 transition-colors"
              >
                Show all
              </button>
            </div>
          )}
          {showExamples && (
            <div
              className="mb-2 flex flex-wrap gap-1.5"
              data-testid="example-prompts"
            >
              {EXAMPLE_PROMPTS.map((group) => (
                <div
                  key={group.group}
                  className="flex flex-wrap items-center gap-1"
                >
                  <span className="text-[10px] text-muted-foreground font-medium mr-1">
                    {group.group}:
                  </span>
                  {group.items.map((p) => (
                    <button
                      key={p}
                      type="button"
                      onClick={() => {
                        setInputValue(p);
                        setShowExamples(false);
                        inputRef.current?.focus();
                      }}
                      className="px-2 py-0.5 rounded text-[10px] bg-muted/30 text-muted-foreground hover:bg-muted/50 transition-colors border border-border/30"
                    >
                      {p}
                    </button>
                  ))}
                </div>
              ))}
              <button
                type="button"
                onClick={() => setShowExamples(false)}
                className="px-2 py-0.5 rounded text-[10px] text-primary hover:text-primary/80 transition-colors"
              >
                Less
              </button>
            </div>
          )}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex gap-3"
          >
            <input
              ref={inputRef}
              className="flex-1 bg-black/20 border border-border/50 rounded-lg px-4 py-2.5 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary/50 placeholder:text-muted-foreground/50 transition-all"
              placeholder="Ask about torrent management..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={isLoading}
              data-testid="chat-input"
            />
            <button
              type="submit"
              disabled={isLoading || !inputValue.trim()}
              data-testid="chat-send"
              className="p-2.5 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/20 shrink-0 disabled:opacity-50 transition-all"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
