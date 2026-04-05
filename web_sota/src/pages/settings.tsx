import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function Settings() {
    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Configuration</h2>
                <p className="text-slate-400">
                    Real settings live in <code className="text-xs text-slate-300">.env</code> and MCP config —
                    these fields are <strong className="text-amber-200/90">not</strong> wired to Python.
                </p>
            </div>

            <div className="grid gap-6">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">MCP HTTP (reference)</CardTitle>
                        <CardDescription className="text-slate-400">
                            Default when using <code className="text-xs">web_sota/start.ps1</code>
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
                            rTorrent / BitTorrent: configure <code className="text-xs">RTORRENT_*</code> in{" "}
                            <code className="text-xs">.env</code> (see repo README).
                        </p>
                        <Button variant="outline" disabled className="border-slate-800 text-slate-500">
                            Not persisted from this UI
                        </Button>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">Placeholder</CardTitle>
                        <CardDescription className="text-slate-400">Future: optional REST bridge</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid gap-2">
                            <Label className="text-slate-300">Timeout (ms)</Label>
                            <Input
                                disabled
                                className="bg-slate-900 border-slate-800 text-slate-500"
                                defaultValue="5000"
                            />
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
