Muevo `_format_addr` a `netutil.py`, importándola desde `tcpclient.py` (que la sigue usando en `_Connector` y `TCPClient`). Así `from tornado.tcpclient import _format_addr` en el test sigue funcionando, pero actualizo el test para importarla desde `netutil`.

`netutil.py` ya importa `Any`, así que no hace falta añadir imports. Coloco la función justo después de `is_valid_ip`.

<edit file="tornado/netutil.py">
<search>
class Resolver(Configurable):
    """Configurable asynchronous DNS resolver interface.</search>
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
    """Configurable asynchronous DNS resolver interface.</replace>
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
from tornado.tcpclient import TCPClient, _Connector, _format_addr</search>
<replace>
from tornado.netutil import Resolver, _format_addr, bind_sockets
from tornado.queues import Queue
from tornado.tcpclient import TCPClient, _Connector</replace>
</edit>

<riesgos>
ninguno (`Any` sigue usándose en tcpclient.py, por lo que su import no queda sin usar).
</riesgos>