import logging
from typing import MutableMapping, Any, Iterable, Optional, Mapping, Iterator


class Application(MutableMapping[str, Any]):

    def __init__(
        self,
        logger: logging.Logger = None,
        middlewares: Iterable = (),
        handler_args: Optional[Mapping[str, Any]] = None,
        client_max_size: int = 1024 ** 2,
        debug: Any = None
    ) -> None:

        if debug is not None:
            self.debug = debug

        self._router = UrlDispatcher()
        self._handler_args = handler_args
        self.logger = logger

        self._middlewares = FrozenList(middlewares)

        # initialized on freezing
        self._middlewares_handlers = tuple()
        # initialized on freezing
        self._run_middlewares = None

        self._state = {}
        self._frozen = False
        self._pre_frozen = False
        self._subapps = []

        self._on_response_prepare = Signal(self)
        self._on_startup = Signal(self)
        self._on_shutdown = Signal(self)
        self._on_cleanup = Signal(self)
        self._cleanup_ctx = CleanupContext()
        self._on_startup.append(self._cleanup_ctx._on_startup)
        self._on_cleanup.append(self._cleanup_ctx._on_cleanup)
        self._client_max_size = client_max_size

    def __eq__(self, other: object) -> bool:
        return self is other

    def __getitem__(self, key: str) -> Any:
        return self._state[key]

    def _check_frozen(self) -> None:
        if self._frozen:
            raise RuntimeError('Changing state of started or joined application is forbidden')

    def __setitem__(self, key: str, value: Any) -> None:
        self._check_frozen()
        self._state[key] = value

    def __delitem__(self, key: str) -> None:
        self._check_frozen()
        del self._state[key]

    def __len__(self) -> int:
        return len(self._state)

    def __iter__(self) -> Iterator[str]:
        return iter(self._state)
