Renombro `is_valid_ip` a `is_ip_address` en su definición (`netutil.py`) y actualizo todas las referencias que aparecen en el contexto: `httpserver.py`, `simple_httpclient.py`, `platform/caresresolver.py`, `test/netutil_test.py` y `test/api.txt`. No renombro el método de prueba `test_is_valid_ip` ni la clase `IsValidIPTest`, porque la orden solo habla de la función.

<edit file="tornado/netutil.py">
<search>
def is_valid_ip(ip: str) -> bool:
</search>
<replace>
def is_ip_address(ip: str) -> bool:
</replace>
</edit>

<edit file="tornado/httpserver.py">
<search>
        if netutil.is_valid_ip(ip):
</search>
<replace>
        if netutil.is_ip_address(ip):
</replace>
</edit>

<edit file="tornado/simple_httpclient.py">
<search>
    _client_ssl_defaults,
    is_valid_ip,
)
</search>
<replace>
    _client_ssl_defaults,
    is_ip_address,
)
</replace>
</edit>

<edit file="tornado/simple_httpclient.py">
<search>
                if is_valid_ip(self.request.network_interface):
</search>
<replace>
                if is_ip_address(self.request.network_interface):
</replace>
</edit>

<edit file="tornado/platform/caresresolver.py">
<search>
from tornado.netutil import Resolver, is_valid_ip
</search>
<replace>
from tornado.netutil import Resolver, is_ip_address
</replace>
</edit>

<edit file="tornado/platform/caresresolver.py">
<search>
        if is_valid_ip(host):
</search>
<replace>
        if is_ip_address(host):
</replace>
</edit>

<edit file="tornado/test/netutil_test.py">
<search>
    bind_sockets,
    is_valid_ip,
)
</search>
<replace>
    bind_sockets,
    is_ip_address,
)
</replace>
</edit>

<edit file="tornado/test/netutil_test.py">
<search>
        self.assertTrue(is_valid_ip("127.0.0.1"))
        self.assertTrue(is_valid_ip("4.4.4.4"))
        self.assertTrue(is_valid_ip("::1"))
        self.assertTrue(is_valid_ip("2620:0:1cfe:face:b00c::3"))
        self.assertFalse(is_valid_ip("www.google.com"))
        self.assertFalse(is_valid_ip("localhost"))
        self.assertFalse(is_valid_ip("4.4.4.4<"))
        self.assertFalse(is_valid_ip(" 127.0.0.1"))
        self.assertFalse(is_valid_ip(""))
        self.assertFalse(is_valid_ip(" "))
        self.assertFalse(is_valid_ip("\n"))
        self.assertFalse(is_valid_ip("\x00"))
        self.assertFalse(is_valid_ip("a" * 100))
</search>
<replace>
        self.assertTrue(is_ip_address("127.0.0.1"))
        self.assertTrue(is_ip_address("4.4.4.4"))
        self.assertTrue(is_ip_address("::1"))
        self.assertTrue(is_ip_address("2620:0:1cfe:face:b00c::3"))
        self.assertFalse(is_ip_address("www.google.com"))
        self.assertFalse(is_ip_address("localhost"))
        self.assertFalse(is_ip_address("4.4.4.4<"))
        self.assertFalse(is_ip_address(" 127.0.0.1"))
        self.assertFalse(is_ip_address(""))
        self.assertFalse(is_ip_address(" "))
        self.assertFalse(is_ip_address("\n"))
        self.assertFalse(is_ip_address("\x00"))
        self.assertFalse(is_ip_address("a" * 100))
</replace>
</edit>

<edit file="tornado/test/api.txt">
<search>
tornado.netutil.is_valid_ip: function(ip)
</search>
<replace>
tornado.netutil.is_ip_address: function(ip)
</replace>
</edit>

<riesgos>
Puede haber referencias fuera del contexto (documentación .rst, `tornado/test/httpserver_test.py` u otros tests) que no pude ver; conviene buscar `is_valid_ip` en todo el repositorio.
</riesgos>