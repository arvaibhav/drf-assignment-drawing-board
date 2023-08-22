import asyncio
import time
from contextlib import contextmanager, asynccontextmanager


class LockInterface:
    def acquire(self, key, timeout=None):
        raise NotImplementedError

    def release(self, key):
        raise NotImplementedError

    # async def acquire_async(self, key, timeout=None):
    #     raise NotImplementedError
    #
    # async def release_async(self, key):
    #     raise NotImplementedError


class InMemoryLock(LockInterface):
    def __init__(self):
        self._locks = {}
        self._async_lock = asyncio.Lock()

    def acquire(self, key, timeout=None):
        end_time = time.time() + (timeout or 0)
        while key in self._locks:
            if timeout is not None and time.time() >= end_time:
                return False
            time.sleep(0.1)
        self._locks[key] = True
        return True

    def release(self, key):
        self._locks.pop(key, None)
