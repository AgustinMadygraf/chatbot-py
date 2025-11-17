#!/usr/bin/env python3
"""Wrapper to run Black with a guaranteed event loop."""
from __future__ import annotations

import asyncio
import sys

from black import patched_main


def main() -> int:
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return patched_main()


if __name__ == "__main__":
    sys.exit(main())
