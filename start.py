#!/usr/bin/env python3
"""Start all services required for the Railway deployment."""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
import shutil

# Commands to launch. The Rasa services are optional and only started when the
# binary is available and not explicitly disabled via environment variables.
RASA_RUN_CMD: List[str] = [
    "rasa",
    "run",
    "--enable-api",
    "--cors",
    "*",
    "--model",
    "rasa_project/models",
    "--endpoints",
    "rasa_project/endpoints.yml",
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


def _is_truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _should_start_rasa(env: Dict[str, str]) -> Tuple[bool, str]:
    if _is_truthy(env.get("DISABLE_RASA")) or _is_truthy(env.get("SKIP_RASA")):
        print("Rasa startup disabled via environment variable.", file=sys.stderr)
        return False, ""

    rasa_binary = RASA_RUN_CMD[0]
    if shutil.which(rasa_binary, path=env.get("PATH")) is None:
        print(
            f"Command '{rasa_binary}' not found. Skipping Rasa startup.",
            file=sys.stderr,
        )
        return False, ""

    model_value = env.get("RASA_MODEL_PATH", "rasa_project/models")
    model_path = Path(model_value)
    if not model_path.is_absolute():
        model_path = Path(__file__).resolve().parent / model_path
    if not model_path.exists():
        print(
            f"Model path '{model_path}' not found. Skipping Rasa startup.",
            file=sys.stderr,
        )
        return False, str(model_path)

    return True, str(model_path)


def _should_start_actions(env: Dict[str, str]) -> bool:
    if _is_truthy(env.get("DISABLE_RASA_ACTIONS")) or _is_truthy(
        env.get("SKIP_RASA_ACTIONS")
    ):
        print("Rasa actions server disabled via environment variable.", file=sys.stderr)
        return False
    return True


def _build_process_plan(
    env: Dict[str, str],
) -> Tuple[List[Tuple[str, List[str]]], Tuple[str, List[str]]]:
    background: List[Tuple[str, List[str]]] = []
    start_rasa, model_path = _should_start_rasa(env)
    if start_rasa:
        background.append(("rasa", _build_rasa_run_cmd(model_path)))
        if _should_start_actions(env):
            background.append(("actions", RASA_ACTIONS_CMD))
    else:
        print(
            "Rasa services will not be started; using FastAPI webhook only.",
            file=sys.stderr,
        )

    foreground: Tuple[str, List[str]] = ("uvicorn", UVICORN_CMD)
    return background, foreground


def _build_rasa_run_cmd(model_path: str) -> List[str]:
    cmd = list(RASA_RUN_CMD)
    try:
        model_index = cmd.index("--model") + 1
    except ValueError:
        return cmd
    cmd[model_index] = model_path
    return cmd


def _prepare_env() -> Dict[str, str]:
    env = os.environ.copy()
    repo_root = str(Path(__file__).resolve().parent)
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f"{repo_root}:{existing}" if existing else repo_root
    print(f"[DEBUG] PYTHONPATH={env['PYTHONPATH']}", file=sys.stderr)
    print(f"[DEBUG] PATH={env.get('PATH')}", file=sys.stderr)
    print(f"[DEBUG] VIRTUAL_ENV={env.get('VIRTUAL_ENV')}", file=sys.stderr)
    print(f"[DEBUG] Python version: {sys.version}", file=sys.stderr)
    return env


class ProcessManager:
    """Utility to spawn services and ensure they terminate gracefully."""

    def __init__(
        self,
        env: Dict[str, str],
        background_processes: Iterable[Tuple[str, List[str]]],
        foreground_process: Tuple[str, List[str]],
    ) -> None:
        self._env = env
        self._background_processes = list(background_processes)
        self._foreground_process = foreground_process
        self._processes: List[Tuple[str, subprocess.Popen[str]]] = []
        self._shutdown_requested = False

    def start_background(self) -> None:
        "Starts all background processes."
        for name, cmd in self._background_processes:
            self._spawn(name, cmd)

    def start_foreground(self) -> subprocess.Popen[str]:
        "Starts the foreground process and returns its Popen instance."
        name, cmd = self._foreground_process
        proc = self._spawn(name, cmd)
        return proc

    def _spawn(self, name: str, cmd: List[str]) -> subprocess.Popen[str]:
        print(f"[DEBUG] Launching process: {name} -> {' '.join(cmd)}", file=sys.stderr)
        proc = subprocess.Popen(cmd, env=self._env)
        self._processes.append((name, proc))
        print(f"[{name}] started with PID {proc.pid}", file=sys.stderr)
        return proc

    def request_shutdown(self) -> None:
        "Requests shutdown of all managed processes."
        if not self._shutdown_requested:
            self._shutdown_requested = True
            print("Shutdown requested, terminating child processes...", file=sys.stderr)
            self._terminate_all()

    def monitor(self, foreground: subprocess.Popen[str]) -> int:
        "Monitors the foreground process and shuts down if any process exits."
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
    "Punto de entrada principal para iniciar todos los servicios."
    env = _prepare_env()
    background_processes, foreground_process = _build_process_plan(env)
    manager = ProcessManager(env, background_processes, foreground_process)

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
