Plan: mover `_format_addr` a `netutil.py` (que ya importa `Any`), importarla en `tcpclient.py` desde `tornado.netutil` y actualizar el test, que importa `_format_addr` desde `tornado.tcpclient`.

En `tcpclient.py`, los usos (`_format_addr(addr)`) siguen funcionando con la importación. El test también seguiría funcionando porque `tcpclient` re-exporta el nombre importado, pero lo actualizo para importarlo desde `netutil`, que es su nueva ubicación.

<edit file="tornado/netutil.py">
<search>
# Default backlog used when calling sock.listen()
_DEFAULT_BACKLOG = 128
</search>
<replace>
# Default backlog used when calling sock.listen()
_DEFAULT_BACKLOG = 128


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
ninguno (`Any` ya se importa en netutil.py y sigue usándose en tcpclient.py; no hay riesgo de importación circular porque tcpclient ya importaba de netutil).
</riesgos>