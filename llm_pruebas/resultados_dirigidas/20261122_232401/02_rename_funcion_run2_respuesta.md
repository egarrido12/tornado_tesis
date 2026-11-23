Renombro `url_concat` a `concat_url_args` en su definición y en todos los lugares donde se usa.

- **Definición:** `tornado/httputil.py`, incluidos los doctests del docstring.
- **Código del paquete:** `tornado/auth.py` (importación y dos usos) y `tornado/web.py` (`RedirectHandler`).
- **Pruebas:** `tornado/test/httputil_test.py` y `tornado/test/auth_test.py`.
- **API pública:** `tornado/test/api.txt`, donde coloco la nueva entrada en el orden alfabético que le corresponde.

Los nombres de los métodos de prueba que contienen `url_concat` los dejo como están, porque no son referencias a la función.

<edit file="tornado/httputil.py">
<search>
def url_concat(
    url: str,
    args: None | dict[str, str] | list[tuple[str, str]] | tuple[tuple[str, str], ...],
) -> str:
    """Concatenate url and arguments regardless of whether
    url has existing query parameters.

    ``args`` may be either a dictionary or a list of key-value pairs
    (the latter allows for multiple values with the same key.

    >>> url_concat("http://example.com/foo", dict(c="d"))
    'http://example.com/foo?c=d'
    >>> url_concat("http://example.com/foo?a=b", dict(c="d"))
    'http://example.com/foo?a=b&c=d'
    >>> url_concat("http://example.com/foo?a=b", [("c", "d"), ("c", "d2")])
</search>
<replace>
def concat_url_args(
    url: str,
    args: None | dict[str, str] | list[tuple[str, str]] | tuple[tuple[str, str], ...],
) -> str:
    """Concatenate url and arguments regardless of whether
    url has existing query parameters.

    ``args`` may be either a dictionary or a list of key-value pairs
    (the latter allows for multiple values with the same key.

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
from tornado.log import gen_log
</search>
<replace>
    concat_url_args,
)
from tornado.log import gen_log
</replace>
</edit>

<edit file="tornado/test/httputil_test.py">
<search>
    def test_url_concat_no_query_params(self):
        url = url_concat(
</search>
<replace>
    def test_url_concat_no_query_params(self):
        url = concat_url_args(
</replace>
</edit>

<edit file="tornado/test/httputil_test.py">
<search>
    def test_url_concat_encode_args(self):
        url = url_concat(
</search>
<replace>
    def test_url_concat_encode_args(self):
        url = concat_url_args(
</replace>
</edit>

<edit file="tornado/test/httputil_test.py">
<search>
    def test_url_concat_trailing_q(self):
        url = url_concat(
</search>
<replace>
    def test_url_concat_trailing_q(self):
        url = concat_url_args(
</replace>
</edit>

<edit file="tornado/test/httputil_test.py">
<search>
    def test_url_concat_q_with_no_trailing_amp(self):
        url = url_concat(
</search>
<replace>
    def test_url_concat_q_with_no_trailing_amp(self):
        url = concat_url_args(
</replace>
</edit>

<edit file="tornado/test/httputil_test.py">
<search>
    def test_url_concat_trailing_amp(self):
        url = url_concat(
</search>
<replace>
    def test_url_concat_trailing_amp(self):
        url = concat_url_args(
</replace>
</edit>

<edit file="tornado/test/httputil_test.py">
<search>
    def test_url_concat_mult_params(self):
        url = url_concat(
</search>
<replace>
    def test_url_concat_mult_params(self):
        url = concat_url_args(
</replace>
</edit>

<edit file="tornado/test/httputil_test.py">
<search>
    def test_url_concat_no_params(self):
        url = url_concat(
</search>
<replace>
    def test_url_concat_no_params(self):
        url = concat_url_args(
</replace>
</edit>

<edit file="tornado/test/httputil_test.py">
<search>
    def test_url_concat_none_params(self):
        url = url_concat(
</search>
<replace>
    def test_url_concat_none_params(self):
        url = concat_url_args(
</replace>
</edit>

<edit file="tornado/test/httputil_test.py">
<search>
    def test_url_concat_with_frag(self):
        url = url_concat(
</search>
<replace>
    def test_url_concat_with_frag(self):
        url = concat_url_args(
</replace>
</edit>

<edit file="tornado/test/httputil_test.py">
<search>
    def test_url_concat_multi_same_params(self):
        url = url_concat(
</search>
<replace>
    def test_url_concat_multi_same_params(self):
        url = concat_url_args(
</replace>
</edit>

<edit file="tornado/test/httputil_test.py">
<search>
    def test_url_concat_multi_same_query_params(self):
        url = url_concat(
</search>
<replace>
    def test_url_concat_multi_same_query_params(self):
        url = concat_url_args(
</replace>
</edit>

<edit file="tornado/test/httputil_test.py">
<search>
    def test_url_concat_dict_params(self):
        url = url_concat(
</search>
<replace>
    def test_url_concat_dict_params(self):
        url = concat_url_args(
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
tornado.httputil.ResponseStartLine.version: attribute
tornado.httputil.doctests: function()
</search>
<replace>
tornado.httputil.ResponseStartLine.version: attribute
tornado.httputil.concat_url_args: function(url, args)
tornado.httputil.doctests: function()
</replace>
</edit>

<riesgos>
Si hay documentación (por ejemplo docs/httputil.rst) u otros archivos fuera del contexto que mencionen `url_concat`, no los he actualizado. Tampoco he podido verificar cómo `api.txt` compara el orden de sus entradas; coloqué la nueva entrada en orden alfabético por si la comparación es literal.
</riesgos>