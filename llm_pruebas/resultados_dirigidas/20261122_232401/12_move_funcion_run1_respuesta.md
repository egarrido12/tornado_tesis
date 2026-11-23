Plan: mover `_format_addr` a `netutil.py` (donde ya existe `from typing import Any`), importarla en `tcpclient.py` para que los usos internos sigan funcionando, y actualizar la importación de la prueba para que apunte al nuevo módulo.

En `tcpclient.py`, `from tornado.netutil import Resolver` pasa a incluir `_format_addr`. La prueba importa `_format_addr` desde `tornado.tcpclient`; ese nombre seguiría funcionando por la importación, pero la actualizo para que apunte a `netutil`.

Coloco la función en `netutil.py` justo después de `is_valid_ip`.

<edit file="tornado/netutil.py">
<search>
class Resolver(Configurable):
    """Configurable asynchronous DNS resolver interface.
</search>
<replace>
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


class Resolver(Configurable):
    """Configurable asynchronous DNS resolver interface.
</replace>
</edit>

<edit file="tornado/tcpclient.py">
<search>
from tornado.netutil import Resolver

_INITIAL_CONNECT_TIMEOUT = 0.3


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
</search>
<replace>
from tornado.netutil import Resolver, _format_addr

_INITIAL_CONNECT_TIMEOUT = 0.3
</replace>
</edit>

<edit file="tornado/test/tcpclient_test.py">
<search>
from tornado.netutil import Resolver, bind_sockets
from tornado.queues import Queue
from tornado.tcpclient import TCPClient, _Connector, _format_addr
</search>
<replace>
from tornado.netutil import Resolver, _format_addr, bind_sockets
from tornado.queues import Queue
from tornado.tcpclient import TCPClient, _Connector
</replace>
</edit>

<riesgos>
ninguno (`Any` sigue usándose en tcpclient.py, así que su importación no queda huérfana).
</riesgos>