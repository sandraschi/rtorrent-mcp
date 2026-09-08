import { useCallback, useEffect, useState } from "react";

const LEVELS = [0.5, 0.6, 0.7, 0.8, 1.0, 1.25, 1.5, 2.0, 3.0] as const;
const STORAGE_KEY = "tauri-zoom";
const DEFAULT_ZOOM = 1.0;

function readStoredZoom(): number {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const parsed = raw ? Number.parseFloat(raw) : DEFAULT_ZOOM;
    return LEVELS.includes(parsed as (typeof LEVELS)[number])
      ? parsed
      : DEFAULT_ZOOM;
  } catch {
    return DEFAULT_ZOOM;
  }
}

function applyZoom(level: number) {
  // WebView2 (Windows Tauri) and dev-browser Chromium both honor the
  // non-standard CSS `zoom` property, which is why this works in both
  // the packaged native app and `vite dev` without a Tauri API call.
  document.body.style.zoom = String(level);
}

/**
 * Tauri windows have no native browser zoom (Ctrl+Scroll/Ctrl+0 do nothing
 * by default), so without this the app is effectively unusable at high-DPI
 * or for anyone who wants larger text. Ctrl+Scroll steps through LEVELS,
 * Ctrl+0 resets to 1.0. Persisted to localStorage so it survives restarts.
 */
export function useZoom() {
  const [zoom, setZoom] = useState<number>(DEFAULT_ZOOM);

  useEffect(() => {
    const initial = readStoredZoom();
    setZoom(initial);
    applyZoom(initial);
  }, []);

  const setLevel = useCallback((level: number) => {
    setZoom(level);
    applyZoom(level);
    try {
      localStorage.setItem(STORAGE_KEY, String(level));
    } catch {
      /* private browsing / storage blocked - zoom still applies this session */
    }
  }, []);

  useEffect(() => {
    const onWheel = (e: WheelEvent) => {
      if (!e.ctrlKey) return;
      e.preventDefault();
      setZoom((current) => {
        const idx = LEVELS.indexOf(current as (typeof LEVELS)[number]);
        const currentIdx = idx === -1 ? LEVELS.indexOf(DEFAULT_ZOOM) : idx;
        const nextIdx =
          e.deltaY < 0
            ? Math.min(currentIdx + 1, LEVELS.length - 1)
            : Math.max(currentIdx - 1, 0);
        const next = LEVELS[nextIdx];
        applyZoom(next);
        try {
          localStorage.setItem(STORAGE_KEY, String(next));
        } catch {
          /* ignore */
        }
        return next;
      });
    };

    const onKeydown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === "0") {
        e.preventDefault();
        setLevel(DEFAULT_ZOOM);
      }
    };

    window.addEventListener("wheel", onWheel, { passive: false });
    window.addEventListener("keydown", onKeydown);
    return () => {
      window.removeEventListener("wheel", onWheel);
      window.removeEventListener("keydown", onKeydown);
    };
  }, [setLevel]);

  return { zoom, setLevel, levels: LEVELS };
}
