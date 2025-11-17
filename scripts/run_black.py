#!/usr/bin/env python3
"""Wrapper to run Black with a guaranteed event loop."""
from __future__ import annotations

import os
import asyncio
import sys

os.environ.setdefault("BLACK_USE_UVLOOP", "0")

from black import patched_main

try:
    from black import concurrency as black_concurrency
except ImportError:  # pragma: no cover - guard for future versions
    black_concurrency = None


def main() -> int:
    if black_concurrency and hasattr(black_concurrency, "maybe_install_uvloop"):
        black_concurrency.maybe_install_uvloop = lambda: False

    class SafeEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
        def get_event_loop(self):  # type: ignore[override]
            try:
                return super().get_event_loop()
            except RuntimeError:
                loop = self.new_event_loop()
                self.set_event_loop(loop)
                return loop

    asyncio.set_event_loop_policy(SafeEventLoopPolicy())
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    return patched_main()


if __name__ == "__main__":
    sys.exit(main())
