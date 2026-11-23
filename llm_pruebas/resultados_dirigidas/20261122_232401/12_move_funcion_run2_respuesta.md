Plan: mover `_format_addr` a `netutil.py` (que ya importa `Any`), importarla en `tcpclient.py` desde `tornado.netutil` y actualizar el test que la importaba desde `tornado.tcpclient`.

Colocación en `netutil.py`: justo antes de `is_valid_ip`, que es un punto estable y único.

En `tcpclient.py`, la importación `from tornado.netutil import Resolver` pasa a incluir `_format_addr`. Los usos en `tcpclient.py` (`on_connect_timeout` y `connect`) siguen funcionando sin cambios, porque el nombre queda importado en ese módulo.

En el test, `from tornado.tcpclient import TCPClient, _Connector, _format_addr` se divide para importar `_format_addr` desde `tornado.netutil`. Como el test ya importa `Resolver, bind_sockets` de `tornado.netutil`, lo añado a esa línea.

<edit file="tornado/netutil.py">
<search>
def is_valid_ip(ip: str) -> bool:
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


def is_valid_ip(ip: str) -> bool:
</replace>
</edit>

<edit file="tornado/tcpclient.py">
<search>
from tornado.netutil import Resolver
</search>
<replace>
from tornado.netutil import Resolver, _format_addr
</replace>
</edit>

<edit file="tornado/tcpclient.py">
<search>
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


class _Connector:
</search>
<replace>
class _Connector:
</replace>
</edit>

<edit file="tornado/test/tcpclient_test.py">
<search>
from tornado.netutil import Resolver, bind_sockets
</search>
<replace>
from tornado.netutil import Resolver, _format_addr, bind_sockets
</replace>
</edit>

<edit file="tornado/test/tcpclient_test.py">
<search>
from tornado.tcpclient import TCPClient, _Connector, _format_addr
</search>
<replace>
from tornado.tcpclient import TCPClient, _Connector
</replace>
</edit>

<riesgos>
No pude ver otros archivos fuera de los mostrados; si algún módulo o prueba más importaba `_format_addr` desde `tornado.tcpclient`, seguirá funcionando mientras `tcpclient` la importe (lo hace), pero conviene comprobarlo. `Any` sigue usándose en `tcpclient.py`, por lo que su importación no queda sin uso.
</riesgos>