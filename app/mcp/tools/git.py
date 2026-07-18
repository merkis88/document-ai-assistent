import asyncio
import subprocess
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

GIT_REPO_PATH: Path | None = None


def configure_git_repo(repo_path: str) -> None:
    global GIT_REPO_PATH

    path = Path(repo_path).expanduser().resolve()

    if not path.exists():
        raise RuntimeError(f"Repository path does not exist: {path}")

    if not path.is_dir():
        raise RuntimeError(f"Repository path is not a directory: {path}")

    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
        )

    except FileNotFoundError as error:
        raise RuntimeError("Git is not installed or not available in PATH") from error

    except subprocess.TimeoutExpired as error:
        raise RuntimeError("Git repository check timed out") from error

    if result.returncode != 0:
        raise RuntimeError(
            f"Path is not a Git repository: {path}. "
            f"Git error: {result.stderr.strip()}"
        )

    GIT_REPO_PATH = Path(result.stdout.strip()).resolve()


def get_git_repo_path() -> Path:
    if GIT_REPO_PATH is None:
        raise RuntimeError("Git repository is not configured")

    return GIT_REPO_PATH


async def run_git_command(
    args: list[str],
    timeout: int = 10,
) -> dict[str, Any]:

    repo_path = get_git_repo_path()

    try:
        process = await asyncio.create_subprocess_exec(
            "git",
            "-C",
            str(repo_path),
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout,
        )

        stdout = stdout_bytes.decode("utf-8", errors="replace").rstrip()
        stderr = stderr_bytes.decode("utf-8", errors="replace").rstrip()

        return {
            "ok": process.returncode == 0,
            "returncode": process.returncode,
            "stdout": stdout,
            "stderr": stderr,
        }

    except asyncio.TimeoutError:
        return {
            "ok": False,
            "error": "Git command timed out",
        }

    except OSError as error:
        return {
            "ok": False,
            "error": f"Git command failed: {str(error)}",
        }


def clamp_text(text: str, max_chars: int) -> dict[str, Any]:
    max_chars = max(500, min(max_chars, 30_000))

    return {
        "text": text[:max_chars],
        "truncated": len(text) > max_chars,
        "returned_chars": min(len(text), max_chars),
    }


def normalize_repo_file_path(file_path: str) -> str:
    file_path = file_path.strip()

    if not file_path:
        raise ValueError("file_path must not be empty")

    raw_path = Path(file_path)

    if raw_path.is_absolute():
        raise ValueError("file_path must be relative")

    repo_path = get_git_repo_path()
    full_path = (repo_path / raw_path).resolve()

    try:
        relative_path = full_path.relative_to(repo_path)

    except ValueError as error:
        raise ValueError("file_path must be inside repository") from error

    return relative_path.as_posix()


def register_git_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def git_current_branch() -> dict[str, Any]:

        result = await run_git_command(
            ["branch", "--show-current"]
        )

        if not result["ok"]:
            return {
                "error": result.get("stderr") or result.get("error"),
            }

        return {
            "repo_path": str(get_git_repo_path()),
            "branch": result["stdout"],
        }

    @mcp.tool()
    async def git_status() -> dict[str, Any]:

        result = await run_git_command(
            ["status", "--short", "--branch"]
        )

        if not result["ok"]:
            return {
                "error": result.get("stderr") or result.get("error"),
            }

        return {
            "repo_path": str(get_git_repo_path()),
            "is_clean": result["stdout"] == "",
            "status": result["stdout"],
        }

    @mcp.tool()
    async def git_log(limit: int = 10) -> dict[str, Any]:

        limit = max(1, min(limit, 50))

        result = await run_git_command(
            [
                "log",
                f"-{limit}",
                "--oneline",
                "--decorate",
            ]
        )

        if not result["ok"]:
            return {
                "error": result.get("stderr") or result.get("error"),
            }

        return {
            "repo_path": str(get_git_repo_path()),
            "limit": limit,
            "commits": result["stdout"],
        }

    @mcp.tool()
    async def git_diff(
        file_path: str | None = None,
        max_chars: int = 12_000,
    ) -> dict[str, Any]:

        args = ["diff"]

        try:
            if file_path:
                safe_path = normalize_repo_file_path(file_path)
                args.extend(["--", safe_path])

        except ValueError as error:
            return {
                "error": str(error),
            }

        result = await run_git_command(args)

        if not result["ok"]:
            return {
                "error": result.get("stderr") or result.get("error"),
            }

        clamped = clamp_text(result["stdout"], max_chars)

        return {
            "repo_path": str(get_git_repo_path()),
            "file_path": file_path,
            "diff": clamped["text"],
            "truncated": clamped["truncated"],
            "returned_chars": clamped["returned_chars"],
        }

    @mcp.tool()
    async def git_staged_diff(
        max_chars: int = 12_000,
    ) -> dict[str, Any]:

        result = await run_git_command(
            ["diff", "--cached"]
        )

        if not result["ok"]:
            return {
                "error": result.get("stderr") or result.get("error"),
            }

        clamped = clamp_text(result["stdout"], max_chars)

        return {
            "repo_path": str(get_git_repo_path()),
            "diff": clamped["text"],
            "truncated": clamped["truncated"],
            "returned_chars": clamped["returned_chars"],
        }

    @mcp.tool()
    async def git_show_commit(
        commit_hash: str,
        max_chars: int = 12_000,
    ) -> dict[str, Any]:

        commit_hash = commit_hash.strip()

        if not commit_hash:
            return {
                "error": "commit_hash must not be empty",
            }

        result = await run_git_command(
            [
                "show",
                "--stat",
                "--patch",
                commit_hash,
            ]
        )

        if not result["ok"]:
            return {
                "error": result.get("stderr") or result.get("error"),
            }

        clamped = clamp_text(result["stdout"], max_chars)

        return {
            "repo_path": str(get_git_repo_path()),
            "commit_hash": commit_hash,
            "content": clamped["text"],
            "truncated": clamped["truncated"],
            "returned_chars": clamped["returned_chars"],
        }