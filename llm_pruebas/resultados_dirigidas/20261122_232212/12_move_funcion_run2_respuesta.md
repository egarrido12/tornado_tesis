Muevo `_format_addr` de `tornado/tcpclient.py` a `tornado/netutil.py`, actualizo la importación en `tcpclient.py` y la del test `tcpclient_test.py`, que la importaba desde `tornado.tcpclient`.

En `netutil.py` la inserto antes de `class Resolver`. `Any` ya está importado allí.

En `tcpclient.py` la función se usa en `on_connect_timeout` y en `connect`, así que importo el nombre desde `netutil` para no tocar esos usos. La importación existente es `from tornado.netutil import Resolver`.

En el test cambio la importación para traer `_format_addr` desde `tornado.netutil`.

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
Sin verificar: otros archivos que importen `_format_addr` desde `tornado.tcpclient` (solo vi el test). `tcpclient.py` sigue exponiendo el nombre vía la importación, así que esas importaciones seguirían funcionando.
</riesgos>