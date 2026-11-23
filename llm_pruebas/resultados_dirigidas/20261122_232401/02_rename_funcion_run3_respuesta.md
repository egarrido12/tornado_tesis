Renombro `url_concat` a `concat_url_args` en su definición (`tornado/httputil.py`, incluidos los doctests de su docstring) y en todos los usos que veo: `auth.py`, `web.py`, `auth_test.py`, `httputil_test.py` y `api.txt`. En `api.txt` muevo la entrada a su posición alfabética, porque el archivo está ordenado.

<edit file="tornado/httputil.py">
<search>
def url_concat(
    url: str,
    args: None | dict[str, str] | list[tuple[str, str]] | tuple[tuple[str, str], ...],
) -> str:</search>
<replace>
def concat_url_args(
    url: str,
    args: None | dict[str, str] | list[tuple[str, str]] | tuple[tuple[str, str], ...],
) -> str:</replace>
</edit>
<edit file="tornado/httputil.py">
<search>
    >>> url_concat("http://example.com/foo", dict(c="d"))
    'http://example.com/foo?c=d'
    >>> url_concat("http://example.com/foo?a=b", dict(c="d"))
    'http://example.com/foo?a=b&c=d'
    >>> url_concat("http://example.com/foo?a=b", [("c", "d"), ("c", "d2")])</search>
<replace>
    >>> concat_url_args("http://example.com/foo", dict(c="d"))
    'http://example.com/foo?c=d'
    >>> concat_url_args("http://example.com/foo?a=b", dict(c="d"))
    'http://example.com/foo?a=b&c=d'
    >>> concat_url_args("http://example.com/foo?a=b", [("c", "d"), ("c", "d2")])</replace>
</edit>
<edit file="tornado/auth.py">
<search>from tornado.httputil import url_concat</search>
<replace>from tornado.httputil import concat_url_args</replace>
</edit>
<edit file="tornado/auth.py">
<search>        handler.redirect(url_concat(url, args))</search>
<replace>        handler.redirect(concat_url_args(url, args))</replace>
</edit>
<edit file="tornado/auth.py">
<search>        return url_concat(url, args)</search>
<replace>        return concat_url_args(url, args)</replace>
</edit>
<edit file="tornado/web.py">
<search>            to_url = httputil.url_concat(</search>
<replace>            to_url = httputil.concat_url_args(</replace>
</edit>
<edit file="tornado/test/auth_test.py">
<search>from tornado.httputil import url_concat</search>
<replace>from tornado.httputil import concat_url_args</replace>
</edit>
<edit file="tornado/test/auth_test.py">
<search>        self.redirect(url_concat(self.get_argument("redirect_uri"), dict(code=code)))</search>
<replace>        self.redirect(
            concat_url_args(self.get_argument("redirect_uri"), dict(code=code))
        )</replace>
</edit>
<edit file="tornado/test/httputil_test.py">
<search>    url_concat,
)
from tornado.log import gen_log</search>
<replace>    concat_url_args,
)
from tornado.log import gen_log</replace>
</edit>
<edit file="tornado/test/httputil_test.py">
<search>    def test_url_concat_no_query_params(self):
        url = url_concat("https://localhost/path", [("y", "y"), ("z", "z")])
        self.assertEqual(url, "https://localhost/path?y=y&z=z")

    def test_url_concat_encode_args(self):
        url = url_concat("https://localhost/path", [("y", "/y"), ("z", "z")])
        self.assertEqual(url, "https://localhost/path?y=%2Fy&z=z")

    def test_url_concat_trailing_q(self):
        url = url_concat("https://localhost/path?", [("y", "y"), ("z", "z")])
        self.assertEqual(url, "https://localhost/path?y=y&z=z")

    def test_url_concat_q_with_no_trailing_amp(self):
        url = url_concat("https://localhost/path?x", [("y", "y"), ("z", "z")])
        self.assertEqual(url, "https://localhost/path?x=&y=y&z=z")

    def test_url_concat_trailing_amp(self):
        url = url_concat("https://localhost/path?x&", [("y", "y"), ("z", "z")])
        self.assertEqual(url, "https://localhost/path?x=&y=y&z=z")

    def test_url_concat_mult_params(self):
        url = url_concat("https://localhost/path?a=1&b=2", [("y", "y"), ("z", "z")])
        self.assertEqual(url, "https://localhost/path?a=1&b=2&y=y&z=z")

    def test_url_concat_no_params(self):
        url = url_concat("https://localhost/path?r=1&t=2", [])
        self.assertEqual(url, "https://localhost/path?r=1&t=2")

    def test_url_concat_none_params(self):
        url = url_concat("https://localhost/path?r=1&t=2", None)
        self.assertEqual(url, "https://localhost/path?r=1&t=2")

    def test_url_concat_with_frag(self):
        url = url_concat("https://localhost/path#tab", [("y", "y")])
        self.assertEqual(url, "https://localhost/path?y=y#tab")

    def test_url_concat_multi_same_params(self):
        url = url_concat("https://localhost/path", [("y", "y1"), ("y", "y2")])
        self.assertEqual(url, "https://localhost/path?y=y1&y=y2")

    def test_url_concat_multi_same_query_params(self):
        url = url_concat("https://localhost/path?r=1&r=2", [("y", "y")])
        self.assertEqual(url, "https://localhost/path?r=1&r=2&y=y")

    def test_url_concat_dict_params(self):
        url = url_concat("https://localhost/path", dict(y="y"))
        self.assertEqual(url, "https://localhost/path?y=y")</search>
<replace>    def test_url_concat_no_query_params(self):
        url = concat_url_args("https://localhost/path", [("y", "y"), ("z", "z")])
        self.assertEqual(url, "https://localhost/path?y=y&z=z")

    def test_url_concat_encode_args(self):
        url = concat_url_args("https://localhost/path", [("y", "/y"), ("z", "z")])
        self.assertEqual(url, "https://localhost/path?y=%2Fy&z=z")

    def test_url_concat_trailing_q(self):
        url = concat_url_args("https://localhost/path?", [("y", "y"), ("z", "z")])
        self.assertEqual(url, "https://localhost/path?y=y&z=z")

    def test_url_concat_q_with_no_trailing_amp(self):
        url = concat_url_args("https://localhost/path?x", [("y", "y"), ("z", "z")])
        self.assertEqual(url, "https://localhost/path?x=&y=y&z=z")

    def test_url_concat_trailing_amp(self):
        url = concat_url_args("https://localhost/path?x&", [("y", "y"), ("z", "z")])
        self.assertEqual(url, "https://localhost/path?x=&y=y&z=z")

    def test_url_concat_mult_params(self):
        url = concat_url_args(
            "https://localhost/path?a=1&b=2", [("y", "y"), ("z", "z")]
        )
        self.assertEqual(url, "https://localhost/path?a=1&b=2&y=y&z=z")

    def test_url_concat_no_params(self):
        url = concat_url_args("https://localhost/path?r=1&t=2", [])
        self.assertEqual(url, "https://localhost/path?r=1&t=2")

    def test_url_concat_none_params(self):
        url = concat_url_args("https://localhost/path?r=1&t=2", None)
        self.assertEqual(url, "https://localhost/path?r=1&t=2")

    def test_url_concat_with_frag(self):
        url = concat_url_args("https://localhost/path#tab", [("y", "y")])
        self.assertEqual(url, "https://localhost/path?y=y#tab")

    def test_url_concat_multi_same_params(self):
        url = concat_url_args("https://localhost/path", [("y", "y1"), ("y", "y2")])
        self.assertEqual(url, "https://localhost/path?y=y1&y=y2")

    def test_url_concat_multi_same_query_params(self):
        url = concat_url_args("https://localhost/path?r=1&r=2", [("y", "y")])
        self.assertEqual(url, "https://localhost/path?r=1&r=2&y=y")

    def test_url_concat_dict_params(self):
        url = concat_url_args("https://localhost/path", dict(y="y"))
        self.assertEqual(url, "https://localhost/path?y=y")</replace>
</edit>
<edit file="tornado/test/api.txt">
<search>tornado.httputil.ResponseStartLine.version: attribute
tornado.httputil.doctests: function()</search>
<replace>tornado.httputil.ResponseStartLine.version: attribute
tornado.httputil.concat_url_args: function(url, args)
tornado.httputil.doctests: function()</replace>
</edit>
<edit file="tornado/test/api.txt">
<search>tornado.httputil.split_host_and_port: function(netloc)
tornado.httputil.url_concat: function(url, args)</search>
<replace>tornado.httputil.split_host_and_port: function(netloc)</replace>
</edit>

<riesgos>
No pude ver otros archivos (docs `.rst`, demos, otros tests) que puedan usar `url_concat`; si existen, hay que actualizarlos. No dejé un alias `url_concat`, así que el código externo que lo importe dejará de funcionar. El orden de `api.txt` asume ordenación ASCII (mayúsculas antes que minúsculas).
</riesgos>