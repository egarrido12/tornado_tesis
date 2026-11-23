Busco las referencias a `_normalize_header` en los archivos del contexto. En `tornado/httputil.py` aparecen la definición (con `@lru_cache`) y sus usos en `HTTPHeaders`: `add`, `get_list`, `__setitem__`, `__contains__`, `__getitem__` y `__delitem__`. Hay una mención más en el doctest de la propia función.

Como cada búsqueda debe coincidir una sola vez en el archivo, uso líneas de contexto distintas en cada edición.

<edit file="tornado/httputil.py">
<search>
def _normalize_header(name: str) -> str:
    """Map a header name to Http-Header-Case.

    >>> _normalize_header("coNtent-TYPE")
</search>
<replace>
def _to_header_case(name: str) -> str:
    """Map a header name to Http-Header-Case.

    >>> _to_header_case("coNtent-TYPE")
</replace>
</edit>
<edit file="tornado/httputil.py">
<search>
        norm_name = _normalize_header(name)
        if norm_name in self:
            self._combined_cache.pop(norm_name, None)
</search>
<replace>
        norm_name = _to_header_case(name)
        if norm_name in self:
            self._combined_cache.pop(norm_name, None)
</replace>
</edit>
<edit file="tornado/httputil.py">
<search>
        norm_name = _normalize_header(name)
        return self._as_list.get(norm_name, [])
</search>
<replace>
        norm_name = _to_header_case(name)
        return self._as_list.get(norm_name, [])
</replace>
</edit>
<edit file="tornado/httputil.py">
<search>
        norm_name = _normalize_header(name)
        self._combined_cache[norm_name] = value
</search>
<replace>
        norm_name = _to_header_case(name)
        self._combined_cache[norm_name] = value
</replace>
</edit>
<edit file="tornado/httputil.py">
<search>
        norm_name = _normalize_header(name)
        return norm_name in self._as_list
</search>
<replace>
        norm_name = _to_header_case(name)
        return norm_name in self._as_list
</replace>
</edit>
<edit file="tornado/httputil.py">
<search>
        header = _normalize_header(name)
</search>
<replace>
        header = _to_header_case(name)
</replace>
</edit>
<edit file="tornado/httputil.py">
<search>
        norm_name = _normalize_header(name)
        # _combined_cache is populated lazily
</search>
<replace>
        norm_name = _to_header_case(name)
        # _combined_cache is populated lazily
</replace>
</edit>

<riesgos>
Solo pude revisar los archivos del contexto; no incluye `tornado/test/`, así que no pude comprobar si alguna prueba o código externo importa `_normalize_header` directamente. Si lo hace, habría que actualizarlo.
</riesgos>