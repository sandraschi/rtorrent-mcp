import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Send, Bot, User } from "lucide-react";

export function Chat() {
    return (
        <div className="flex h-[calc(100vh-8rem)] flex-col space-y-4">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Command interface (mock)</h2>
                    <p className="text-slate-400">
                        This input does <strong className="text-amber-200/90">not</strong> call the MCP. Use your
                        agent (Cursor / Claude) with the rTorrent MCP for real BitTorrent commands.
                    </p>
                </div>
            </div>

            <Card className="flex-1 border-slate-800 bg-slate-950/50 flex flex-col overflow-hidden opacity-90">
                <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
                    <div className="flex gap-3">
                        <div className="h-8 w-8 rounded-full bg-slate-800 flex items-center justify-center border border-slate-700">
                            <User className="h-4 w-4 text-slate-400" />
                        </div>
                        <div className="flex-1 space-y-1">
                            <div className="flex items-center gap-2">
                                <span className="text-sm font-medium text-slate-200">Example</span>
                                <span className="text-xs text-slate-500">static transcript</span>
                            </div>
                            <p className="text-sm text-slate-500 bg-slate-900/50 p-3 rounded-md border border-slate-800 inline-block">
                                Illustrative message — not sent to any API.
                            </p>
                        </div>
                    </div>

                    <div className="flex gap-3">
                        <div className="h-8 w-8 rounded-full bg-blue-900/20 flex items-center justify-center border border-blue-800">
                            <Bot className="h-4 w-4 text-blue-400" />
                        </div>
                        <div className="flex-1 space-y-1">
                            <div className="flex items-center gap-2">
                                <span className="text-sm font-medium text-blue-400">Example</span>
                                <span className="text-xs text-slate-500">placeholder</span>
                            </div>
                            <div className="text-sm text-slate-500 bg-blue-950/10 p-3 rounded-md border border-blue-900/30 inline-block">
                                <p>Hook <code className="text-xs">fetch</code> to your bridge if you build one.</p>
                            </div>
                        </div>
                    </div>
                </CardContent>
                <div className="p-4 border-t border-slate-800 bg-slate-900/30">
                    <div className="flex gap-2">
                        <input
                            disabled
                            className="flex-1 bg-slate-950 border border-slate-800 rounded-md px-4 py-2 text-sm text-slate-500 cursor-not-allowed"
                            placeholder="Not connected — use MCP in your IDE"
                        />
                        <Button size="icon" disabled className="bg-slate-700">
                            <Send className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </Card>
        </div>
    );
}
