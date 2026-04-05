'use client';

import { APPS_CATALOG } from '@/common/apps-catalog';
import { useMcpBackendStatus } from '@/hooks/useMcpBackendStatus';
import { LayoutGrid, ExternalLink, HelpCircle } from 'lucide-react';
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';

export function Topbar() {
    const mcp = useMcpBackendStatus();

    const mcpLabel =
        mcp === "checking"
            ? "MCP HTTP…"
            : mcp === "reachable"
              ? "MCP HTTP up"
              : "MCP HTTP down";

    const mcpClass =
        mcp === "checking"
            ? "bg-slate-500/10 text-slate-400 border-slate-500/20"
            : mcp === "reachable"
              ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
              : "bg-rose-500/10 text-rose-400 border-rose-500/20";

    return (
        <header className="flex h-14 items-center justify-between border-b border-slate-800 bg-slate-950/50 px-6 backdrop-blur-xl">
            <div className="flex items-center gap-4">
                <h1 className="text-sm font-medium text-slate-400">
                    Navigation / <span className="text-slate-100">rTorrent MCP shell</span>
                </h1>
            </div>

            <div className="flex items-center gap-2">
                <div
                    className={`mr-4 flex items-center gap-2 rounded-full px-3 py-1 text-xs border ${mcpClass}`}
                    title="Backend on 10910: /api/health + /mcp (start web_sota/start.ps1)"
                >
                    <span className="relative flex h-2 w-2">
                        {mcp === "reachable" ? (
                            <>
                                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                                <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
                            </>
                        ) : mcp === "checking" ? (
                            <span className="relative inline-flex h-2 w-2 rounded-full bg-slate-500" />
                        ) : (
                            <span className="relative inline-flex h-2 w-2 rounded-full bg-rose-500" />
                        )}
                    </span>
                    {mcpLabel}
                </div>

                {/* Global Apps Navigation */}
                <DropdownMenu.Root>
                    <DropdownMenu.Trigger asChild>
                        <button className="flex items-center gap-2 rounded-md border border-slate-800 bg-slate-900/50 px-3 py-1.5 text-sm text-slate-300 hover:bg-slate-800 transition-colors focus:outline-none focus:ring-2 focus:ring-slate-700">
                            <LayoutGrid className="h-4 w-4" />
                            Apps
                        </button>
                    </DropdownMenu.Trigger>

                    <DropdownMenu.Portal>
                        <DropdownMenu.Content
                            className="z-50 min-w-[220px] animate-in fade-in zoom-in-95 data-[side=bottom]:slide-in-from-top-2 rounded-md border border-slate-800 bg-slate-950 p-1 shadow-xl"
                            sideOffset={5}
                            align="end"
                        >
                            <DropdownMenu.Label className="px-2 py-1.5 text-xs font-semibold text-slate-500">
                                Switch Application
                            </DropdownMenu.Label>

                            <div className="h-px bg-slate-800 my-1" />

                            {APPS_CATALOG.map((app) => (
                                <DropdownMenu.Item key={app.id} asChild>
                                    <a
                                        href={app.url}
                                        className="flex w-full select-none items-center rounded-sm px-2 py-1.5 text-sm text-slate-300 hover:bg-slate-800 hover:text-white focus:bg-slate-800 focus:text-white outline-none cursor-pointer"
                                    >
                                        <app.icon className="mr-2 h-4 w-4 text-slate-400" />
                                        <span>{app.label}</span>
                                        <ExternalLink className="ml-auto h-3 w-3 opacity-50" />
                                    </a>
                                </DropdownMenu.Item>
                            ))}
                        </DropdownMenu.Content>
                    </DropdownMenu.Portal>
                </DropdownMenu.Root>

                <button className="flex h-8 w-8 items-center justify-center rounded-md border border-slate-800 bg-slate-900/50 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors">
                    <HelpCircle className="h-4 w-4" />
                </button>
            </div>
        </header>
    );
}
