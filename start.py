#!/usr/bin/env python3
"""Start all services required for the Railway deployment."""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Commands to launch. The first two stay in the background while the last one
# (uvicorn) keeps the container alive for Railway's health checks.
RASA_RUN_CMD: List[str] = [
    "rasa",
    "run",
    "--enable-api",
    "--cors",
    "*",
    "--model",
    "rasa_project/models",
    "--port",
    "5005",
    "--debug",
]

RASA_ACTIONS_CMD: List[str] = [
    "rasa",
    "run",
    "actions",
    "--actions",
    "rasa_project.actions.actions",
    "--port",
    "5055",
]

UVICORN_CMD: List[str] = [
    "uvicorn",
    "main:app",
    "--host",
    "0.0.0.0",
    "--port",
    "8080",
    "--proxy-headers",
]

BACKGROUND_PROCESSES: List[Tuple[str, List[str]]] = [
    ("rasa", RASA_RUN_CMD),
    ("actions", RASA_ACTIONS_CMD),
]

FOREGROUND_PROCESS: Tuple[str, List[str]] = ("uvicorn", UVICORN_CMD)


def _prepare_env() -> Dict[str, str]:
    env = os.environ.copy()
    repo_root = str(Path(__file__).resolve().parent)
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f"{repo_root}:{existing}" if existing else repo_root
    return env


class ProcessManager:
    """Utility to spawn services and ensure they terminate gracefully."""

    def __init__(self, env: Dict[str, str]) -> None:
        self._env = env
        self._processes: List[Tuple[str, subprocess.Popen[str]]] = []
        self._shutdown_requested = False

    def start_background(self) -> None:
        for name, cmd in BACKGROUND_PROCESSES:
            self._spawn(name, cmd)

    def start_foreground(self) -> subprocess.Popen[str]:
        name, cmd = FOREGROUND_PROCESS
        proc = self._spawn(name, cmd)
        return proc

    def _spawn(self, name: str, cmd: List[str]) -> subprocess.Popen[str]:
        proc = subprocess.Popen(cmd, env=self._env)
        self._processes.append((name, proc))
        print(f"[{name}] started with PID {proc.pid}", file=sys.stderr)
        return proc

    def request_shutdown(self) -> None:
        if not self._shutdown_requested:
            self._shutdown_requested = True
            print("Shutdown requested, terminating child processes...", file=sys.stderr)
            self._terminate_all()

    def monitor(self, foreground: subprocess.Popen[str]) -> int:
        try:
            while True:
                if foreground.poll() is not None:
                    return foreground.returncode or 0

                for name, proc in self._processes:
                    if proc is foreground:
                        continue
                    code = proc.poll()
                    if code is not None:
                        print(
                            f"[{name}] exited with code {code}. Stopping remaining services...",
                            file=sys.stderr,
                        )
                        self.request_shutdown()
                        return code or 1

                time.sleep(1)
        except KeyboardInterrupt:
            print("Received keyboard interrupt.", file=sys.stderr)
            self.request_shutdown()
            return 130

    def _terminate_all(self) -> None:
        deadline = time.monotonic() + 10
        for name, proc in self._processes:
            if proc.poll() is None:
                print(f"Sending SIGTERM to {name} (PID {proc.pid})", file=sys.stderr)
                try:
                    proc.terminate()
                except ProcessLookupError:
                    continue

        for name, proc in self._processes:
            if proc.poll() is not None:
                continue
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            try:
                proc.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                continue

        for name, proc in self._processes:
            if proc.poll() is None:
                print(f"Sending SIGKILL to {name} (PID {proc.pid})", file=sys.stderr)
                try:
                    proc.kill()
                except ProcessLookupError:
                    continue

        for _, proc in self._processes:
            if proc.poll() is None:
                try:
                    proc.wait()
                except subprocess.TimeoutExpired:
                    continue


def main() -> int:
    env = _prepare_env()
    manager = ProcessManager(env)

    def _signal_handler(signum: int, _frame) -> None:
        print(f"Received signal {signum}; shutting down.", file=sys.stderr)
        manager.request_shutdown()

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, _signal_handler)

    manager.start_background()
    foreground = manager.start_foreground()

    exit_code = manager.monitor(foreground)
    manager.request_shutdown()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
