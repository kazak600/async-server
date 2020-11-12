import asyncio
import collections


class AsyncStreamIterator(Generic[_T]):
    def __init__(self, read_func: Callable[[], Awaitable[_T]]) -> None:
        self.read_func = read_func

    def __aiter__(self) -> "AsyncStreamIterator[_T]":
        return self

    async def __anext__(self) -> _T:
        try:
            rv = await self.read_func()
        except Exception:
            raise StopAsyncIteration
        if rv == b"":
            raise StopAsyncIteration
        return rv


class StreamReader(AsyncStreamReaderMixin):

    def __init__(
        self,
        protocol: BaseProtocol,
        limit: int,
        *,
        timer: Optional[BaseTimerContext] = None,
        loop: asyncio.AbstractEventLoop
    ) -> None:
        self._protocol = protocol
        self._low_water = limit
        self._high_water = limit * 2
        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop
        self._size = 0
        self._cursor = 0
        self._http_chunk_splits = None  # type: Optional[List[int]]
        self._buffer = collections.deque()  # type: Deque[bytes]
        self._buffer_offset = 0
        self._eof = False
        self._waiter = None  # type: Optional[asyncio.Future[None]]
        self._eof_waiter = None  # type: Optional[asyncio.Future[None]]
        self._exception = None  # type: Optional[BaseException]
        self._timer = timer
        self._eof_callbacks = []  # type: List[Callable[[], None]]
