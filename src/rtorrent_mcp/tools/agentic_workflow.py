"""
FastMCP 3.1 agentic workflow: sampling with tools (SEP-1577-style).

Requires ctx.sample_step and a configured sampling handler (or client LLM).
"""

from __future__ import annotations

import logging

from fastmcp import Context

logger = logging.getLogger(__name__)


def _ok(**kwargs: object) -> dict:
    return {
        "success": True,
        "operation": kwargs.get("operation", "unknown"),
        "summary": kwargs.get("summary", "Operation completed"),
        "result": kwargs.get("result", {}),
        "next_steps": kwargs.get("next_steps", []),
    }


def _err(**kwargs: object) -> dict:
    return {
        "success": False,
        "error": kwargs.get("error", "Unknown error"),
        "error_code": kwargs.get("error_code", "UNKNOWN"),
        "message": kwargs.get("message", ""),
        "recovery_options": kwargs.get("recovery_options", []),
    }


def register_agentic_rtorrent_workflow(app) -> None:
    """Register ``agentic_rtorrent_workflow`` on the FastMCP app."""

    @app.tool()
    async def agentic_rtorrent_workflow(
        workflow_prompt: str,
        available_tools: list[str],
        max_iterations: int = 8,
        context: Context | None = None,
    ) -> dict:
        """
        RTORRENT_AGENTIC_WORKFLOW — Multi-step torrent/search automation via sampling with tools.

        PORTMANTEAU PATTERN RATIONALE: One entry point for LLM-orchestrated flows (search, add,
        legal check) without hard-coding sequences in the client.

        Args:
            workflow_prompt: What to accomplish in natural language (e.g. search Nyaa and add best match).
            available_tools: Tool names the LLM may call (e.g. torrent_management, search_management).
            max_iterations: Max LLM rounds (default 8).

        Returns:
            Structured dict with success, result.final_output, executed_tools, iterations.
        """
        try:
            if not workflow_prompt.strip():
                return _err(
                    error="Missing workflow_prompt",
                    error_code="MISSING_PROMPT",
                    message="workflow_prompt is required",
                    recovery_options=["Describe the task clearly"],
                )
            if not available_tools:
                return _err(
                    error="No tools specified",
                    error_code="EMPTY_TOOLS",
                    message="Pass at least one portmanteau tool name",
                    recovery_options=[
                        "Example: ['search_management','torrent_management','legal_management']"
                    ],
                )
            if context is None or not hasattr(context, "sample_step"):
                return _err(
                    error="Sampling unavailable",
                    error_code="SAMPLING_UNAVAILABLE",
                    message="Context has no sample_step (needs FastMCP 3.1+ and sampling)",
                    recovery_options=[
                        "Install fastmcp>=3.1",
                        "Configure RTORRENT_SAMPLING_* or RTORRENT_SAMPLING_USE_CLIENT_LLM=1",
                    ],
                )

            all_tools = await app.list_tools()
            name_to_tool = {t.name: t for t in all_tools if hasattr(t, "name")}
            tools_for_sampling = [name_to_tool[n] for n in available_tools if n in name_to_tool]
            missing = [n for n in available_tools if n not in name_to_tool]
            if missing:
                logger.warning("agentic_rtorrent_workflow: unknown tool names: %s", missing)
            if not tools_for_sampling:
                return _err(
                    error="No matching tools",
                    error_code="TOOLS_NOT_FOUND",
                    message=f"None of available_tools matched. Registered: {list(name_to_tool.keys())}",
                    recovery_options=["Use names from system_management(action='help') or docs"],
                )

            system_prompt = (
                "You are an rTorrent automation assistant. Use the provided MCP tools only. "
                "Prefer search_management before torrent_management(add). "
                "Respect legal_management for jurisdiction questions. Summarize results briefly."
            )
            messages: list = [{"role": "user", "content": workflow_prompt}]
            executed: list[str] = []
            iterations = 0
            step = None

            while iterations < max_iterations:
                iterations += 1
                step = await context.sample_step(
                    messages,
                    system_prompt=system_prompt,
                    tools=tools_for_sampling,
                    execute_tools=True,
                    max_tokens=4096,
                )
                if hasattr(step, "history") and step.history:
                    messages = list(step.history)
                if hasattr(step, "tool_calls") and step.tool_calls:
                    for tc in step.tool_calls:
                        name = getattr(tc, "name", None) or getattr(tc, "tool_name", str(tc))
                        if name:
                            executed.append(name)
                if not getattr(step, "is_tool_use", True):
                    final_text = getattr(step, "text", "") or ""
                    return _ok(
                        operation="agentic_rtorrent_workflow",
                        summary=f"Completed in {iterations} round(s).",
                        result={
                            "final_output": final_text,
                            "iterations": iterations,
                            "executed_tools": list(dict.fromkeys(executed)),
                        },
                        next_steps=["Verify rTorrent and downloads in your client."],
                    )

            return _ok(
                operation="agentic_rtorrent_workflow",
                summary=f"Stopped after {max_iterations} iterations (limit).",
                result={
                    "final_output": getattr(step, "text", "") if step else "",
                    "iterations": iterations,
                    "executed_tools": list(dict.fromkeys(executed)),
                },
                next_steps=["Raise max_iterations or narrow the workflow_prompt."],
            )
        except Exception as e:
            logger.exception("agentic_rtorrent_workflow failed")
            return _err(
                error="Workflow failed",
                error_code="WORKFLOW_ERROR",
                message=str(e),
                recovery_options=["Check rTorrent connectivity", "Check sampling LLM"],
            )
