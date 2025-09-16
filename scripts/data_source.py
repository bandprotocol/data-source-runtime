#!/usr/bin/env python3

import sys
import ccxt
import aiohttp
import asyncio
import os
import time

if __name__ == "__main__":
    try:
        time.sleep(5)
        print(sys.argv[1:])
        print(os.getpid())
        print(globals())
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
