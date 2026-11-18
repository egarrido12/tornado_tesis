```python
#
# Copyright 2014 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""A non-blocking TCP connection factory."""

import asyncio
import datetime
import functools
import numbers
import socket
import ssl
from collections.abc import Callable, Iterator
from typing import Any

from tornado import gen
from tornado.concurrent import Future, future_add_done_callback
from tornado.ioloop import IOLoop
from tornado.iostream import IOStream
from tornado.netutil import Resolver

_INITIAL_CONNECT_TIMEOUT = 0.3

# A list of (address family, socket address) pairs, as produced by
# `_Connector.split`.
_AddressList = list[tuple[socket.AddressFamily, tuple[Any, ...]]]


def _format_addr(addr: Any) -> str:
    """Format a socket address for use in error messages.

    IPv4 addresses are formatted as ``1.2.3.4:443`` and IPv6 addresses as
    ``[::1]:443``. Anything else is formatted with `str`.
    """
    if isinstance(addr, tuple) and len(addr) >= 2:
        host, port = addr[:2]
        if isinstance(host, str) and ":" in host:
            return f"[{host}]:{port}"
        return f"{host}:{port}"
    return str(addr)


def _to_absolute_deadline(
    timeout: float | datetime.timedelta,
) -> float:
    """Converts a relative ``timeout`` to an absolute `.IOLoop.time` deadline.

    Both numbers and `datetime.timedelta` objects are interpreted as
    durations relative to now.
    """
    if isinstance(timeout, numbers.Real):
        return IOLoop.current().time() + timeout
    elif isinstance(timeout, datetime.timedelta):
        return IOLoop.current().time() + timeout.total_seconds()
    raise TypeError("Unsupported timeout %r" % timeout)


def _failed_future(exc: BaseException) -> "Future[IOStream]":
    """Returns a `.Future` that has already failed with ``exc``."""
    future: Future[IOStream] = Future()
    future.set_exception(exc)
    return future


class _Connector:
    """A stateless implementation of the "Happy Eyeballs" algorithm.

    "Happy Eyeballs" is documented in RFC6555 as the recommended practice
    for when both IPv4 and IPv6 addresses are available.

    In this implementation, we partition the addresses by family, and
    make the first connection attempt to whichever address was
    returned first by ``getaddrinfo``.  If that connection fails or
    times out, we begin a connection in parallel to the first address
    of the other family.  If there are additional failures we retry
    with other addresses, keeping one connection attempt per family
    in flight at a time.

    http://tools.ietf.org/html/rfc6555

    """

    def __init__(
        self,
        addrinfo: list[tuple[Any, ...]],
        connect: Callable[
            [socket.AddressFamily, tuple[Any, ...]], tuple[IOStream, "Future[IOStream]"]
        ],
    ) -> None:
        self.io_loop = IOLoop.current()
        self.connect = connect

        self.future: Future[tuple[socket.AddressFamily, Any, IOStream]] = Future()
        self.timeout: object | None = None
        self.connect_timeout: object | None = None
        self.last_error: Exception | None = None
        self.remaining = len(addrinfo)
        self.primary_addrs, self.secondary_addrs = self.split(addrinfo)
        self.streams: set[IOStream] = set()
        # Addresses with connection attempts in progress. Used for
        # error messages.
        self.pending_addrs: set[tuple[Any, ...]] = set()

    @staticmethod
    def split(
        addrinfo: list[tuple[Any, ...]],
    ) -> tuple[_AddressList, _AddressList]:
        """Partition the ``addrinfo`` list by address family.

        Returns two lists.  The first list contains the first entry from
        ``addrinfo`` and all others with the same family, and the
        second list contains all other addresses (normally one list will
        be AF_INET and the other AF_INET6, although non-standard resolvers
        may return additional families).
        """
        primary = []
        secondary = []
        primary_af = addrinfo[0][0]
        for af, addr in addrinfo:
            if af == primary_af:
                primary.append((af, addr))
            else:
                secondary.append((af, addr))
        return primary, secondary

    def start(
        self,
        timeout: float = _INITIAL_CONNECT_TIMEOUT,
        connect_timeout: float | datetime.timedelta | None = None,
    ) -> "Future[tuple[socket.AddressFamily, Any, IOStream]]":
        # Set the timeouts first: try_connect may fail synchronously, and
        # on_connect_done will then skip ahead to the secondary addresses.
        self.set_timeout(timeout)
        if connect_timeout is not None:
            self.set_connect_timeout(connect_timeout)
        self.try_connect(iter(self.primary_addrs))
        future_add_done_callback(self.future, self.on_future_done)
        return self.future

    def try_connect(self, addrs: Iterator[tuple[socket.AddressFamily, tuple[Any, ...]]]) -> None:
        try:
            af, addr = next(addrs)
        except StopIteration:
            # We've reached the end of our queue, but the other queue
            # might still be working.  Send a final error on the future
            # only when both queues are finished.
            if self.remaining == 0 and not self.future.done():
                self.future.set_exception(
                    self.last_error or IOError("connection failed")
                )
                # Every attempt has finished, but a cancelled attempt's
                # stream may still be open.
                self.close_streams()
            return
        try:
            stream, future = self.connect(af, addr)
        except Exception as e:
            # Report synchronous errors (e.g. an address family that is
            # not supported on this system) through the same path as
            # asynchronous ones, so we move on to the next address.
            future = _failed_future(e)
        else:
            self.streams.add(stream)
            self.pending_addrs.add(addr)
        future_add_done_callback(
            future, functools.partial(self.on_connect_done, addrs, af, addr)
        )

    def on_connect_done(
        self,
        addrs: Iterator[tuple[socket.AddressFamily, tuple[Any, ...]]],
        af: socket.AddressFamily,
        addr: tuple[Any, ...],
        future: "Future[IOStream]",
    ) -> None:
        self.remaining -= 1
        self.pending_addrs.discard(addr)
        try:
            stream = future.result()
        except (Exception, asyncio.CancelledError) as e:
            if self.future.done():
                return
            # Error: try again (but remember what happened so we have an
            # error to raise in the end). A cancelled attempt is treated
            # as a failure, but is not reported as the error because
            # our caller has not been cancelled.
            if not isinstance(e, asyncio.CancelledError):
                self.last_error = e
            self.try_connect(addrs)
            if self.timeout is not None:
                # If the first attempt failed, don't wait for the
                # timeout to try an address from the secondary queue.
                self.io_loop.remove_timeout(self.timeout)
                self.on_timeout()
            return
        self.clear_timeouts()
        if self.future.done():
            # This is a late arrival; just drop it.
            stream.close()
        else:
            self.streams.discard(stream)
            self.future.set_result((af, addr, stream))
            self.close_streams()

    def on_future_done(
        self, future: "Future[tuple[socket.AddressFamily, Any, IOStream]]"
    ) -> None:
        if future.cancelled():
            # The caller gave up (e.g. asyncio.wait_for). Close any
            # connection attempts that are still in progress instead of
            # leaving them open until the OS gives up on them.
            self.clear_timeouts()
            self.close_streams()

    def set_timeout(self, timeout: float) -> None:
        self.timeout = self.io_loop.add_timeout(
            self.io_loop.time() + timeout, self.on_timeout
        )

    def on_timeout(self) -> None:
        self.timeout = None
        if not self.future.done():
            self.try_connect(iter(self.secondary_addrs))

    def clear_timeout(self) -> None:
        if self.timeout is not None:
            self.io_loop.remove_timeout(self.timeout)

    def set_connect_timeout(self, connect_timeout: float | datetime.timedelta) -> None:
        self.connect_timeout = self.io_loop.add_timeout(
            connect_timeout, self.on_connect_timeout
        )

    def _connect_timeout_message(self) -> str:
        if self.pending_addrs:
            addresses = ", ".join(
                sorted(_format_addr(addr) for addr in self.pending_addrs)
            )
            return "Timeout while connecting to %s" % addresses
        return "Timeout while connecting"

    def on_connect_timeout(self) -> None:
        if not self.future.done():
            self.future.set_exception(TimeoutError(self._connect_timeout_message()))
        self.close_streams()

    def clear_timeouts(self) -> None:
        self.clear_timeout()
        if self.connect_timeout is not None:
            self.io_loop.remove_timeout(self.connect_timeout)

    def close_streams(self) -> None:
        for stream in self.streams:
            stream.close()


class TCPClient:
    """A non-blocking TCP connection factory.

    .. versionchanged:: 5.0
       The ``io_loop`` argument (deprecated since version 4.1) has been removed.
    """

    def __init__(self, resolver: Resolver | None = None) -> None:
        if resolver is not None:
            self.resolver = resolver
            self._own_resolver = False
        else:
            self.resolver = Resolver()
            self._own_resolver = True

    def close(self) -> None:
        if self._own_resolver:
            self.resolver.close()

    async def connect(
        self,
        host: str,
        port: int,
        af: socket.AddressFamily = socket.AF_UNSPEC,
        ssl_options: dict[str, Any] | ssl.SSLContext | None = None,
        max_buffer_size: int | None = None,
        source_ip: str | None = None,
        source_port: int | None = None,
        timeout: float | datetime.timedelta | None = None,
    ) -> IOStream:
        """Connect to the given host and port.

        Asynchronously returns an `.IOStream` (or `.SSLIOStream` if
        ``ssl_options`` is not None).

        Using the ``source_ip`` kwarg, one can specify the source
        IP address to use when establishing the connection.
        In case the user needs to resolve and
        use a specific interface, it has to be handled outside
        of Tornado as this depends very much on the platform.

        Raises `TimeoutError` if the input future does not complete before
        ``timeout``, which may be specified in any form allowed by
        `.IOLoop.add_timeout` (i.e. a `datetime.timedelta` or an absolute time
        relative to `.IOLoop.time`)

        The message of the `TimeoutError` indicates which phase of the
        connection timed out: resolving the hostname, establishing the TCP
        connection (listing the addresses being tried), or performing the
        TLS handshake.

        Similarly, when the user requires a certain source port, it can
        be specified using the ``source_port`` arg.

        .. versionchanged:: 4.5
           Added the ``source_ip`` and ``source_port`` arguments.

        .. versionchanged:: 5.0
           Added the ``timeout`` argument.

        .. versionchanged:: 6.6
           Timeout errors now have messages describing which phase of
           the connection process timed out.
        """
        deadline = None if timeout is None else _to_absolute_deadline(timeout)
        addrinfo = await self._resolve(host, port, af, deadline)
        connector = _Connector(
            addrinfo,
            functools.partial(
                self._create_stream,
                max_buffer_size,
                source_ip=source_ip,
                source_port=source_port,
            ),
        )
        _, addr, stream = await connector.start(connect_timeout=deadline)
        # TODO: For better performance we could cache the (af, addr)
        # information here and reuse it on subsequent connections to
        # the same host. (http://tools.ietf.org/html/rfc6555#section-4.2)
        if ssl_options is not None:
            stream = await self._start_tls(stream, host, addr, ssl_options, deadline)
        return stream

    async def _resolve(
        self, host: str, port: int, af: socket.AddressFamily, deadline: float | None
    ) -> list[tuple[int, Any]]:
        """Resolves ``host``, failing if ``deadline`` passes first."""
        resolution = self.resolver.resolve(host, port, af)
        if deadline is None:
            return await resolution
        return await gen.with_timeout(
            deadline,
            resolution,
            message=f"Timeout while resolving {host}",
        )

    async def _start_tls(
        self,
        stream: IOStream,
        host: str,
        addr: Any,
        ssl_options: dict[str, Any] | ssl.SSLContext,
        deadline: float | None,
    ) -> IOStream:
        """Upgrades a connected ``stream`` to TLS, honoring ``deadline``."""
        tls_future = stream.start_tls(
            False, ssl_options=ssl_options, server_hostname=host
        )
        try:
            if deadline is None:
                return await tls_future
            return await gen.with_timeout(
                deadline,
                tls_future,
                message=lambda: "Timeout during TLS handshake with "
                + _format_addr(addr),
            )
        finally:
            # If we're exiting early (timeout or cancellation), cancel
            # the handshake so the new SSLIOStream (which now owns the
            # socket) is closed. with_timeout does not do this for us.
            # This is a no-op if the handshake has already completed.
            tls_future.cancel()

    def _create_stream(
        self,
        max_buffer_size: int | None,
        af: socket.AddressFamily,
        addr: tuple[Any, ...],
        source_ip: str | None = None,
        source_port: int | None = None,
    ) -> tuple[IOStream, "Future[IOStream]"]:
        # Always connect in plaintext; we'll convert to ssl if necessary
        # after one connection has completed.
        bind_port = source_port if isinstance(source_port, int) else 0
        bind_ip = source_ip
        if bind_port and not source_ip:
            # User required a specific port, but did not specify
            # a certain source IP, so bind to the default loopback of the
            # same address family as the requested af socket:
            # - 127.0.0.1 for IPv4
            # - ::1 for IPv6
            bind_ip = "::1" if af == socket.AF_INET6 else "127.0.0.1"
        socket_obj = socket.socket(af)
        try:
            if bind_port or bind_ip:
                # If the user requires binding also to a specific IP/port.
                socket_obj.bind((bind_ip, bind_port))
            stream = IOStream(socket_obj, max_buffer_size=max_buffer_size)
        except BaseException:
            socket_obj.close()
            raise
        return stream, stream.connect(addr)
```

## Refactorizaciones aplicadas

- **Extract Method** — `TCPClient.connect` → nuevos `TCPClient._resolve` y `TCPClient._start_tls`. `connect` mezclaba conversión de timeouts, resolución DNS, Happy Eyeballs y handshake TLS. Ahora cada fase tiene su método y `connect` se lee como una secuencia. El orden de las operaciones, los mensajes de `TimeoutError` y el `tls_future.cancel()` en `finally` no cambian.

- **Extract Function** — `connect` → nueva función de módulo `_to_absolute_deadline`. Aísla la conversión de `timeout` (número o `timedelta`) a un instante absoluto del `IOLoop`, con el mismo `TypeError` para tipos no soportados. Se eliminó además el segundo `if timeout is not None` redundante.

- **Rename Variable** — `connect`: `timeout` pasa a `deadline` dentro del cuerpo. Representa un instante absoluto y no una duración, y el nombre anterior inducía a error. El parámetro público `timeout` conserva su nombre. En `_create_stream`, `source_port_bind` y `source_ip_bind` pasan a `bind_port` y `bind_ip`.

- **Replace Temp with Underscore / Remove Dead Assignment** — `connect`: `af, addr, stream = ...` pasa a `_, addr, stream = ...`, porque `af` se sobrescribía sin volver a usarse.

- **Extract Method** — `_Connector.on_connect_timeout` → nuevo `_Connector._connect_timeout_message`. Separa la construcción del mensaje de la acción de fallar el future y cerrar los streams.

- **Extract Function** — `_Connector.try_connect` → nueva función `_failed_future`. Reemplaza las tres líneas que creaban un `Future` y le asignaban una excepción para el caso síncrono.

- **Reuse Method (eliminar duplicación)** — `_Connector.clear_timeouts` ahora llama a `clear_timeout()` en vez de repetir su lógica.

- **Introduce Type Alias / Replace Duplicated Type** — Nuevo `_AddressList` para el tipo `list[tuple[socket.AddressFamily, tuple[Any, ...]]]`, repetido en `split`. Se eliminó la dependencia de `typing.Tuple` a favor de `tuple[...]`, coherente con el resto del módulo, y la anotación de `start` y `on_future_done` usa `tuple`.

- **Reordenar comentarios (Move Statement)** — `_create_stream`: los comentarios sobre el loopback por defecto estaban después del código que explicaban; ahora van antes. La lógica es idéntica.

Los nombres y firmas públicos (`TCPClient.connect`, `close`, `_Connector.split`, `start`, `try_connect`, `on_*`, `set_*`, `clear_*`, `close_streams` y sus atributos) no cambian, porque los tests los usan directamente.