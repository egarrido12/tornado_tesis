Renombro `Configurable` a `ConfigurableBase` en `tornado/util.py` y actualizo sus referencias en `httpclient.py`, `httpserver.py`, `ioloop.py`, `netutil.py`, `test/util_test.py` y `test/api.txt`.

Hay un detalle importante: dentro de la clase se usa el atributo con name mangling `__impl_class`. Al cambiar el nombre de la clase, el nombre interno pasa de `_Configurable__impl_class` a `_ConfigurableBase__impl_class`. Por eso actualizo también la cadena literal en `configured_class`; si no, el comportamiento cambiaría.

Dos firmas de `configure` superaban las 88 columnas con el nombre nuevo, así que las partí al estilo de black.

<edit file="tornado/util.py">
<search>
The one public-facing part of this module is the `Configurable` class
and its `~Configurable.configure` method, which becomes a part of the
</search>
<replace>
The one public-facing part of this module is the `ConfigurableBase` class
and its `~ConfigurableBase.configure` method, which becomes a part of the
</replace>
</edit>
<edit file="tornado/util.py">
<search>
class Configurable:
    """Base class for configurable interfaces.
</search>
<replace>
class ConfigurableBase:
    """Base class for configurable interfaces.
</replace>
</edit>
<edit file="tornado/util.py">
<search>
    Configurable subclasses must define the class methods
</search>
<replace>
    ConfigurableBase subclasses must define the class methods
</replace>
</edit>
<edit file="tornado/util.py">
<search>
    # because they need to refer to Configurable, which isn't defined
</search>
<replace>
    # because they need to refer to ConfigurableBase, which isn't defined
</replace>
</edit>
<edit file="tornado/util.py">
<search>
    __impl_class: type[Configurable] | None = None
</search>
<replace>
    __impl_class: type[ConfigurableBase] | None = None
</replace>
</edit>
<edit file="tornado/util.py">
<search>
    def configurable_base(cls) -> type[Configurable]:
</search>
<replace>
    def configurable_base(cls) -> type[ConfigurableBase]:
</replace>
</edit>
<edit file="tornado/util.py">
<search>
    def configurable_default(cls) -> type[Configurable]:
</search>
<replace>
    def configurable_default(cls) -> type[ConfigurableBase]:
</replace>
</edit>
<edit file="tornado/util.py">
<search>
    def configure(cls, impl: None | str | type[Configurable], **kwargs: Any) -> None:
</search>
<replace>
    def configure(
        cls, impl: None | str | type[ConfigurableBase], **kwargs: Any
    ) -> None:
</replace>
</edit>
<edit file="tornado/util.py">
<search>
            impl = typing.cast(type[Configurable], import_object(impl))
</search>
<replace>
            impl = typing.cast(type[ConfigurableBase], import_object(impl))
</replace>
</edit>
<edit file="tornado/util.py">
<search>
    def configured_class(cls) -> type[Configurable]:
</search>
<replace>
    def configured_class(cls) -> type[ConfigurableBase]:
</replace>
</edit>
<edit file="tornado/util.py">
<search>
        if base.__dict__.get("_Configurable__impl_class") is None:
</search>
<replace>
        if base.__dict__.get("_ConfigurableBase__impl_class") is None:
</replace>
</edit>
<edit file="tornado/util.py">
<search>
    ) -> tuple[type[Configurable] | None, dict[str, Any] | None]:
</search>
<replace>
    ) -> tuple[type[ConfigurableBase] | None, dict[str, Any] | None]:
</replace>
</edit>
<edit file="tornado/util.py">
<search>
        cls, saved: tuple[type[Configurable] | None, dict[str, Any] | None]
</search>
<replace>
        cls, saved: tuple[type[ConfigurableBase] | None, dict[str, Any] | None]
</replace>
</edit>
<edit file="tornado/httpclient.py">
<search>
from tornado.util import Configurable
</search>
<replace>
from tornado.util import ConfigurableBase
</replace>
</edit>
<edit file="tornado/httpclient.py">
<search>
class AsyncHTTPClient(Configurable):
</search>
<replace>
class AsyncHTTPClient(ConfigurableBase):
</replace>
</edit>
<edit file="tornado/httpclient.py">
<search>
    def configurable_base(cls) -> type[Configurable]:
</search>
<replace>
    def configurable_base(cls) -> type[ConfigurableBase]:
</replace>
</edit>
<edit file="tornado/httpclient.py">
<search>
    def configurable_default(cls) -> type[Configurable]:
</search>
<replace>
    def configurable_default(cls) -> type[ConfigurableBase]:
</replace>
</edit>
<edit file="tornado/httpclient.py">
<search>
        cls, impl: "Union[None, str, Type[Configurable]]", **kwargs: Any
</search>
<replace>
        cls, impl: "Union[None, str, Type[ConfigurableBase]]", **kwargs: Any
</replace>
</edit>
<edit file="tornado/httpserver.py">
<search>
from tornado.util import Configurable
</search>
<replace>
from tornado.util import ConfigurableBase
</replace>
</edit>
<edit file="tornado/httpserver.py">
<search>
class HTTPServer(TCPServer, Configurable, httputil.HTTPServerConnectionDelegate):
</search>
<replace>
class HTTPServer(TCPServer, ConfigurableBase, httputil.HTTPServerConnectionDelegate):
</replace>
</edit>
<edit file="tornado/httpserver.py">
<search>
       `HTTPServer` is now a subclass of `tornado.util.Configurable`.
</search>
<replace>
       `HTTPServer` is now a subclass of `tornado.util.ConfigurableBase`.
</replace>
</edit>
<edit file="tornado/httpserver.py">
<search>
    def configurable_base(cls) -> type[Configurable]:
</search>
<replace>
    def configurable_base(cls) -> type[ConfigurableBase]:
</replace>
</edit>
<edit file="tornado/httpserver.py">
<search>
    def configurable_default(cls) -> type[Configurable]:
</search>
<replace>
    def configurable_default(cls) -> type[ConfigurableBase]:
</replace>
</edit>
<edit file="tornado/ioloop.py">
<search>
from tornado.util import Configurable, import_object
</search>
<replace>
from tornado.util import ConfigurableBase, import_object
</replace>
</edit>
<edit file="tornado/ioloop.py">
<search>
class IOLoop(Configurable):
</search>
<replace>
class IOLoop(ConfigurableBase):
</replace>
</edit>
<edit file="tornado/ioloop.py">
<search>
    def configure(cls, impl: None | str | type[Configurable], **kwargs: Any) -> None:
</search>
<replace>
    def configure(
        cls, impl: None | str | type[ConfigurableBase], **kwargs: Any
    ) -> None:
</replace>
</edit>
<edit file="tornado/ioloop.py">
<search>
    def configurable_base(cls) -> type[Configurable]:
</search>
<replace>
    def configurable_base(cls) -> type[ConfigurableBase]:
</replace>
</edit>
<edit file="tornado/ioloop.py">
<search>
    def configurable_default(cls) -> type[Configurable]:
</search>
<replace>
    def configurable_default(cls) -> type[ConfigurableBase]:
</replace>
</edit>
<edit file="tornado/netutil.py">
<search>
from tornado.util import Configurable, errno_from_exception
</search>
<replace>
from tornado.util import ConfigurableBase, errno_from_exception
</replace>
</edit>
<edit file="tornado/netutil.py">
<search>
class Resolver(Configurable):
</search>
<replace>
class Resolver(ConfigurableBase):
</replace>
</edit>
<edit file="tornado/netutil.py">
<search>
    `Resolver.configure <.Configurable.configure>`
</search>
<replace>
    `Resolver.configure <.ConfigurableBase.configure>`
</replace>
</edit>
<edit file="tornado/test/util_test.py">
<search>
    Configurable,
    GzipDecompressor,
</search>
<replace>
    ConfigurableBase,
    GzipDecompressor,
</replace>
</edit>
<edit file="tornado/test/util_test.py">
<search>
class TestConfigurable(Configurable):
</search>
<replace>
class TestConfigurable(ConfigurableBase):
</replace>
</edit>
<edit file="tornado/test/api.txt">
<search>
tornado.httpclient.AsyncHTTPClient: class(tornado.util.Configurable)
</search>
<replace>
tornado.httpclient.AsyncHTTPClient: class(tornado.util.ConfigurableBase)
</replace>
</edit>
<edit file="tornado/test/api.txt">
<search>
tornado.httpserver.HTTPServer: class(tornado.tcpserver.TCPServer, tornado.util.Configurable, tornado.httputil.HTTPServerConnectionDelegate)
</search>
<replace>
tornado.httpserver.HTTPServer: class(tornado.tcpserver.TCPServer, tornado.util.ConfigurableBase, tornado.httputil.HTTPServerConnectionDelegate)
</replace>
</edit>
<edit file="tornado/test/api.txt">
<search>
tornado.ioloop.IOLoop: class(tornado.util.Configurable)
</search>
<replace>
tornado.ioloop.IOLoop: class(tornado.util.ConfigurableBase)
</replace>
</edit>
<edit file="tornado/test/api.txt">
<search>
tornado.netutil.Resolver: class(tornado.util.Configurable)
</search>
<replace>
tornado.netutil.Resolver: class(tornado.util.ConfigurableBase)
</replace>
</edit>
<edit file="tornado/test/api.txt">
<search>
tornado.util.Configurable: class()
tornado.util.Configurable.__new__: staticmethod(cls, *args, **kwargs)
tornado.util.Configurable.configurable_base: classmethod(cls)
tornado.util.Configurable.configurable_default: classmethod(cls)
tornado.util.Configurable.configure: classmethod(cls, impl, **kwargs)
tornado.util.Configurable.configured_class: classmethod(cls)
tornado.util.Configurable.initialize: method(self)
</search>
<replace>
tornado.util.ConfigurableBase: class()
tornado.util.ConfigurableBase.__new__: staticmethod(cls, *args, **kwargs)
tornado.util.ConfigurableBase.configurable_base: classmethod(cls)
tornado.util.ConfigurableBase.configurable_default: classmethod(cls)
tornado.util.ConfigurableBase.configure: classmethod(cls, impl, **kwargs)
tornado.util.ConfigurableBase.configured_class: classmethod(cls)
tornado.util.ConfigurableBase.initialize: method(self)
</replace>
</edit>

<riesgos>
Sólo pude revisar los archivos del contexto. Otros módulos o pruebas no mostrados (p. ej. `tornado/platform/*`, `tornado/test/*`, la documentación en `docs/`) podrían importar `Configurable` desde `tornado.util` y fallarían hasta actualizarse. No dejé un alias de compatibilidad porque la orden no lo pide.
</riesgos>