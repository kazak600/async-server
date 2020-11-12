import asyncio
import collections


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
