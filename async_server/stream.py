import asyncio
import collections

from typing import Generic, Callable, Awaitable, TypeVar, Optional, Tuple


_Type = TypeVar("_Type")


class AsyncStreamIterator(Generic[_Type]):

    def __init__(self, read_func: Callable[[], Awaitable[_Type]]) -> None:
        self.read_func = read_func

    def __aiter__(self) -> "AsyncStreamIterator[_Type]":
        return self

    async def __anext__(self) -> _Type:
        try:
            rv = await self.read_func()
        except Exception:
            raise StopAsyncIteration
        if rv == b"":
            raise StopAsyncIteration
        return rv


class ChunkTupleAsyncStreamIterator:

    def __init__(self, stream: "StreamReader") -> None:
        self._stream = stream

    def __aiter__(self) -> "ChunkTupleAsyncStreamIterator":
        return self

    async def __anext__(self) -> Tuple[bytes, bool]:
        rv = await self._stream.read_chunk()
        if rv == (b"", False):
            raise StopAsyncIteration
        return rv


class StreamReader:

    def __init__(
        self,
        protocol: BaseProtocol,
        limit: int,
        timer: Optional[BaseTimerContext] = None,
        loop: asyncio.AbstractEventLoop = None
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

    def __aiter__(self) -> AsyncStreamIterator[bytes]:
        return AsyncStreamIterator(self.readline)  # type: ignore

    def iter_chunked(self, n: int) -> AsyncStreamIterator[bytes]:
        """Returns an asynchronous iterator that yields chunks of size n.
        Python-3.5 available for Python 3.5+ only
        """
        return AsyncStreamIterator(lambda: self.read(n))  # type: ignore

    def iter_any(self) -> AsyncStreamIterator[bytes]:
        """Returns an asynchronous iterator that yields all the available
        data as soon as it is received
        Python-3.5 available for Python 3.5+ only
        """
        return AsyncStreamIterator(self.readany)  # type: ignore

    def iter_chunks(self) -> ChunkTupleAsyncStreamIterator:
        """Returns an asynchronous iterator that yields chunks of data
        as they are received by the server. The yielded objects are tuples
        of (bytes, bool) as returned by the StreamReader.readchunk method.
        Python-3.5 available for Python 3.5+ only
        """
        return ChunkTupleAsyncStreamIterator(self)  # type: ignore

    async def read_chunk(self):
        return b"", True
