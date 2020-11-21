def run_app(
    app: Union[Application, Awaitable[Application]],
    *,
    debug: bool = False,
    host: Optional[Union[str, HostSequence]] = None,
    port: Optional[int] = None,
    path: Optional[str] = None,
    sock: Optional[socket.socket] = None,
    shutdown_timeout: float = 60.0,
    keepalive_timeout: float = 75.0,
    ssl_context: Optional[SSLContext] = None,
    print: Optional[Callable[..., None]] = print,
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
                print=print,
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
