import logging
from typing import MutableMapping, Any, Iterable, Optional, Mapping


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
