Renombro `url_concat` a `concat_url_args` en su definición (`tornado/httputil.py`), incluidos los doctests de su docstring, y actualizo todas las referencias que aparecen en el contexto: `auth.py`, `web.py`, los dos archivos de pruebas y `tornado/test/api.txt`. En `api.txt` coloco la entrada en su posición alfabética (antes de `doctests`), por si la comprobación de la API depende del orden.

<edit file="tornado/httputil.py">
<search>
def url_concat(
</search>
<replace>
def concat_url_args(
</replace>
</edit>
<edit file="tornado/httputil.py">
<search>
    >>> url_concat("http://example.com/foo", dict(c="d"))
    'http://example.com/foo?c=d'
    >>> url_concat("http://example.com/foo?a=b", dict(c="d"))
    'http://example.com/foo?a=b&c=d'
    >>> url_concat("http://example.com/foo?a=b", [("c", "d"), ("c", "d2")])
</search>
<replace>
    >>> concat_url_args("http://example.com/foo", dict(c="d"))
    'http://example.com/foo?c=d'
    >>> concat_url_args("http://example.com/foo?a=b", dict(c="d"))
    'http://example.com/foo?a=b&c=d'
    >>> concat_url_args("http://example.com/foo?a=b", [("c", "d"), ("c", "d2")])
</replace>
</edit>
<edit file="tornado/auth.py">
<search>
from tornado.httputil import url_concat
</search>
<replace>
from tornado.httputil import concat_url_args
</replace>
</edit>
<edit file="tornado/auth.py">
<search>
        handler.redirect(url_concat(url, args))
</search>
<replace>
        handler.redirect(concat_url_args(url, args))
</replace>
</edit>
<edit file="tornado/auth.py">
<search>
        return url_concat(url, args)
</search>
<replace>
        return concat_url_args(url, args)
</replace>
</edit>
<edit file="tornado/web.py">
<search>
            to_url = httputil.url_concat(
</search>
<replace>
            to_url = httputil.concat_url_args(
</replace>
</edit>
<edit file="tornado/test/auth_test.py">
<search>
from tornado.httputil import url_concat
</search>
<replace>
from tornado.httputil import concat_url_args
</replace>
</edit>
<edit file="tornado/test/auth_test.py">
<search>
        self.redirect(url_concat(self.get_argument("redirect_uri"), dict(code=code)))
</search>
<replace>
        self.redirect(
            concat_url_args(self.get_argument("redirect_uri"), dict(code=code))
        )
</replace>
</edit>
<edit file="tornado/test/httputil_test.py">
<search>
    url_concat,
)
</search>
<replace>
    concat_url_args,
)
</replace>
</edit>
<edit file="tornado/test/httputil_test.py">
<search>
        url = url_concat("https://localhost/path", [("y", "y"), ("z", "z")])
</search>
<replace>
        url = concat_url_args("https://localhost/path", [("y", "y"), ("z", "z")])
</replace>
</edit>
<edit file="tornado/test/httputil_test.py">
<search>
        url = url_concat("https://localhost/path", [("y", "/y"), ("z", "z")])
</search>
<replace>
        url = concat_url_args("https://localhost/path", [("y", "/y"), ("z", "z")])
</replace>
</edit>
<edit file="tornado/test/httputil_test.py">
<search>
        url = url_concat("https://localhost/path?", [("y", "y"), ("z", "z")])
</search>
<replace>
        url = concat_url_args("https://localhost/path?", [("y", "y"), ("z", "z")])
</replace>
</edit>
<edit file="tornado/test/httputil_test.py">
<search>
        url = url_concat("https://localhost/path?x", [("y", "y"), ("z", "z")])
</search>
<replace>
        url = concat_url_args("https://localhost/path?x", [("y", "y"), ("z", "z")])
</replace>
</edit>
<edit file="tornado/test/httputil_test.py">
<search>
        url = url_concat("https://localhost/path?x&", [("y", "y"), ("z", "z")])
</search>
<replace>
        url = concat_url_args("https://localhost/path?x&", [("y", "y"), ("z", "z")])
</replace>
</edit>
<edit file="tornado/test/httputil_test.py">
<search>
        url = url_concat("https://localhost/path?a=1&b=2", [("y", "y"), ("z", "z")])
</search>
<replace>
        url = concat_url_args(
            "https://localhost/path?a=1&b=2", [("y", "y"), ("z", "z")]
        )
</replace>
</edit>
<edit file="tornado/test/httputil_test.py">
<search>
        url = url_concat("https://localhost/path?r=1&t=2", [])
</search>
<replace>
        url = concat_url_args("https://localhost/path?r=1&t=2", [])
</replace>
</edit>
<edit file="tornado/test/httputil_test.py">
<search>
        url = url_concat("https://localhost/path?r=1&t=2", None)
</search>
<replace>
        url = concat_url_args("https://localhost/path?r=1&t=2", None)
</replace>
</edit>
<edit file="tornado/test/httputil_test.py">
<search>
        url = url_concat("https://localhost/path#tab", [("y", "y")])
</search>
<replace>
        url = concat_url_args("https://localhost/path#tab", [("y", "y")])
</replace>
</edit>
<edit file="tornado/test/httputil_test.py">
<search>
        url = url_concat("https://localhost/path", [("y", "y1"), ("y", "y2")])
</search>
<replace>
        url = concat_url_args("https://localhost/path", [("y", "y1"), ("y", "y2")])
</replace>
</edit>
<edit file="tornado/test/httputil_test.py">
<search>
        url = url_concat("https://localhost/path?r=1&r=2", [("y", "y")])
</search>
<replace>
        url = concat_url_args("https://localhost/path?r=1&r=2", [("y", "y")])
</replace>
</edit>
<edit file="tornado/test/httputil_test.py">
<search>
        url = url_concat("https://localhost/path", dict(y="y"))
</search>
<replace>
        url = concat_url_args("https://localhost/path", dict(y="y"))
</replace>
</edit>
<edit file="tornado/test/api.txt">
<search>
tornado.httputil.split_host_and_port: function(netloc)
tornado.httputil.url_concat: function(url, args)
</search>
<replace>
tornado.httputil.split_host_and_port: function(netloc)
</replace>
</edit>
<edit file="tornado/test/api.txt">
<search>
tornado.httputil.doctests: function()
</search>
<replace>
tornado.httputil.concat_url_args: function(url, args)
tornado.httputil.doctests: function()
</replace>
</edit>

<riesgos>
Puede haber referencias a `url_concat` fuera del contexto recibido (otras pruebas, demos, documentación .rst, notas de versión) que no he podido actualizar. `tornado/test/api.txt` es un archivo generado: si la comprobación de la API exige un orden concreto distinto del alfabético, habría que regenerarlo.
</riesgos>