#!/usr/bin/env python3
"""Wrapper to run Black with a guaranteed event loop."""
from __future__ import annotations

import asyncio
import sys

from black import patched_main

try:
    from black import concurrency as black_concurrency
except ImportError:  # pragma: no cover - guard for future versions
    black_concurrency = None


def main() -> int:
    if black_concurrency and hasattr(black_concurrency, "maybe_install_uvloop"):
        black_concurrency.maybe_install_uvloop = lambda: None

    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return patched_main()


if __name__ == "__main__":
    sys.exit(main())
