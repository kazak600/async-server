import asyncio
import socket
import logging

from ssl import SSLContext
from typing import Optional, Union, Callable, Set, Awaitable, Type

from async_server.web_app import Application


class AppRunner:

    def __init__(self, app, handle_signals, access_log_class, access_log_format, access_log, keepalive_timeout):
        self.app = app
        self.handle_signals = handle_signals
        self.access_log_class = access_log_class
        self.access_log_format = access_log_format
        self.access_log = access_log
        self.keepalive_timeout = keepalive_timeout

    async def setup(self):
        raise NotImplementedError()


class TCPSite:

    def __init__(self, runner, host, port, shutdown_timeout, ssl_context,
                 backlog, reuse_address, reuse_port):

        self.runner = runner
        self.host = host
        self.port = port
        self.shutdown_timeout = shutdown_timeout
        self.ssl_context = ssl_context
        self.backlog = backlog
        self.reuse_address = reuse_address
        self.reuse_port = reuse_port


async def _run_app(
    app: Union[Application, Awaitable[Application]],
    *,
    host: Optional[Union[str, HostSequence]] = None,
    port: Optional[int] = None,
    path: Optional[str] = None,
    sock: Optional[socket.socket] = None,
    shutdown_timeout: float = 60.0,
    keepalive_timeout: float = 75.0,
    ssl_context: Optional[SSLContext] = None,
    print_func: Optional[Callable[..., None]] = None,
    backlog: int = 128,
    access_log_class: Type[AbstractAccessLogger] = AccessLogger,
    access_log_format: str = AccessLogger.LOG_FORMAT,
    access_log: Optional[logging.Logger] = access_logger,
    handle_signals: bool = True,
    reuse_address: Optional[bool] = None,
    reuse_port: Optional[bool] = None,
) -> None:
    if asyncio.iscoroutine(app):
        app = await app  # type: ignore

    if print_func is None:
        print_func = print

    app = cast(Application, app)

    runner = AppRunner(
        app=app,
        handle_signals=handle_signals,
        access_log_class=access_log_class,
        access_log_format=access_log_format,
        access_log=access_log,
        keepalive_timeout=keepalive_timeout,
    )

    await runner.setup()

    sites = []

    try:
        if host is not None:
            if isinstance(host, (str, bytes, bytearray, memoryview)):
                sites.append(
                    TCPSite(
                        runner=runner,
                        host=host,
                        port=port,
                        shutdown_timeout=shutdown_timeout,
                        ssl_context=ssl_context,
                        backlog=backlog,
                        reuse_address=reuse_address,
                        reuse_port=reuse_port,
                    )
                )
    finally:
        pass


def _cancel_tasks(
    to_cancel: Set["asyncio.Task[Any]"], loop: asyncio.AbstractEventLoop
) -> None:
    if not to_cancel:
        return

    for task in to_cancel:
        task.cancel()

    loop.run_until_complete(
        asyncio.gather(*to_cancel, loop=loop, return_exceptions=True)
    )

    for task in to_cancel:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler(
                {
                    "message": "unhandled exception during asyncio.run() shutdown",
                    "exception": task.exception(),
                    "task": task,
                }
            )


class GracefulExit(Exception):
    pass


def run_app(
    app: Union[Application, Awaitable[Application]],
    debug: bool = False,
    host: Optional[Union[str, HostSequence]] = None,
    port: Optional[int] = None,
    path: Optional[str] = None,
    sock: Optional[socket.socket] = None,
    shutdown_timeout: float = 60.0,
    keepalive_timeout: float = 75.0,
    ssl_context: Optional[SSLContext] = None,
    print_func: Optional[Callable[..., None]] = None,
    backlog: int = 128,
    access_log_class: Type[AbstractAccessLogger] = AccessLogger,
    access_log_format: str = AccessLogger.LOG_FORMAT,
    access_log: Optional[logging.Logger] = access_logger,
    handle_signals: bool = True,
    reuse_address: Optional[bool] = None,
    reuse_port: Optional[bool] = None,
) -> None:
    """Run an app locally"""
    loop = asyncio.get_event_loop()
    loop.set_debug(debug)

    # Configure if and only if in debugging mode and using the default logger
    if loop.get_debug() and access_log and access_log.name == "aiohttp.access":
        if access_log.level == logging.NOTSET:
            access_log.setLevel(logging.DEBUG)
        if not access_log.hasHandlers():
            access_log.addHandler(logging.StreamHandler())

    try:
        main_task = loop.create_task(
            _run_app(
                app,
                host=host,
                port=port,
                path=path,
                sock=sock,
                shutdown_timeout=shutdown_timeout,
                keepalive_timeout=keepalive_timeout,
                ssl_context=ssl_context,
                print_func=print_func,
                backlog=backlog,
                access_log_class=access_log_class,
                access_log_format=access_log_format,
                access_log=access_log,
                handle_signals=handle_signals,
                reuse_address=reuse_address,
                reuse_port=reuse_port,
            )
        )
        loop.run_until_complete(main_task)
    except (GracefulExit, KeyboardInterrupt):  # pragma: no cover
        pass
    finally:
        _cancel_tasks({main_task}, loop)
        _cancel_tasks(all_tasks(loop), loop)
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        asyncio.set_event_loop(None)
