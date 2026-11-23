Renombro el parámetro `plus` de `url_escape` a `use_plus` en su definición, su docstring y su cuerpo. `url_unescape` conserva su parámetro `plus`. Actualizo también los llamadores que usan la palabra clave: `tornado/routing.py`, `tornado/test/escape_test.py`, `tornado/test/property_test.py` y la firma registrada en `tornado/test/api.txt`.

<edit file="tornado/escape.py">
<search>
def url_escape(value: str | bytes, plus: bool = True) -> str:
    """Returns a URL-encoded version of the given value.

    Equivalent to either `urllib.parse.quote_plus` or `urllib.parse.quote` depending on the ``plus``
    argument.

    If ``plus`` is true (the default), spaces will be represented as ``+`` and slashes will be
    represented as ``%2F``.  This is appropriate for query strings. If ``plus`` is false, spaces
    will be represented as ``%20`` and slashes are left as-is. This is appropriate for the path
    component of a URL. Note that the default of ``plus=True`` is effectively the
    reverse of Python's urllib module.

    .. versionadded:: 3.1
        The ``plus`` argument
    """
    quote = urllib.parse.quote_plus if plus else urllib.parse.quote
</search>
<replace>
def url_escape(value: str | bytes, use_plus: bool = True) -> str:
    """Returns a URL-encoded version of the given value.

    Equivalent to either `urllib.parse.quote_plus` or `urllib.parse.quote` depending on the ``use_plus``
    argument.

    If ``use_plus`` is true (the default), spaces will be represented as ``+`` and slashes will be
    represented as ``%2F``.  This is appropriate for query strings. If ``use_plus`` is false, spaces
    will be represented as ``%20`` and slashes are left as-is. This is appropriate for the path
    component of a URL. Note that the default of ``use_plus=True`` is effectively the
    reverse of Python's urllib module.

    .. versionadded:: 3.1
        The ``use_plus`` argument
    """
    quote = urllib.parse.quote_plus if use_plus else urllib.parse.quote
</replace>
</edit>

<edit file="tornado/routing.py">
<search>
            converted_args.append(url_escape(utf8(a), plus=False))
</search>
<replace>
            converted_args.append(url_escape(utf8(a), use_plus=False))
</replace>
</edit>

<edit file="tornado/test/escape_test.py">
<search>
        self.assertEqual(url_escape(unescaped, plus=False), escaped)
</search>
<replace>
        self.assertEqual(url_escape(unescaped, use_plus=False), escaped)
</replace>
</edit>

<edit file="tornado/test/property_test.py">
<search>
        escaped = url_escape(s, plus=plus)
</search>
<replace>
        escaped = url_escape(s, use_plus=plus)
</replace>
</edit>

<edit file="tornado/test/property_test.py">
<search>
        self.assertEqual(url_unescape(url_escape(b, plus=plus), None, plus=plus), b)
</search>
<replace>
        self.assertEqual(
            url_unescape(url_escape(b, use_plus=plus), None, plus=plus), b
        )
</replace>
</edit>

<edit file="tornado/test/api.txt">
<search>
tornado.escape.url_escape: function(value, plus=True)
</search>
<replace>
tornado.escape.url_escape: function(value, use_plus=True)
</replace>
</edit>

<riesgos>
No pude buscar en archivos que no se me mostraron (por ejemplo otros tests, demos o la documentación en `docs/`). Si alguno llama a `url_escape(..., plus=...)` por palabra clave, dejará de funcionar y habrá que actualizarlo.
</riesgos>