Busco las referencias a `_normalize_header` en los archivos visibles. En `tornado/httputil.py` aparece en la definición, en un doctest dentro de su docstring y en los métodos de `HTTPHeaders` (`add`, `get_list`, `__setitem__`, `__contains__`, `__getitem__`, `__delitem__`). En el resto de archivos no hay referencias.

Cada bloque `<search>` incluye contexto suficiente para que el texto aparezca una sola vez.

<edit file="tornado/httputil.py">
<search>
@lru_cache(1000)
def _normalize_header(name: str) -> str:
    """Map a header name to Http-Header-Case.

    >>> _normalize_header("coNtent-TYPE")</search>
<replace>
@lru_cache(1000)
def _to_header_case(name: str) -> str:
    """Map a header name to Http-Header-Case.

    >>> _to_header_case("coNtent-TYPE")</replace>
</edit>
<edit file="tornado/httputil.py">
<search>
        norm_name = _normalize_header(name)
        if norm_name in self:
            self._combined_cache.pop(norm_name, None)</search>
<replace>
        norm_name = _to_header_case(name)
        if norm_name in self:
            self._combined_cache.pop(norm_name, None)</replace>
</edit>
<edit file="tornado/httputil.py">
<search>
        norm_name = _normalize_header(name)
        return self._as_list.get(norm_name, [])</search>
<replace>
        norm_name = _to_header_case(name)
        return self._as_list.get(norm_name, [])</replace>
</edit>
<edit file="tornado/httputil.py">
<search>
        norm_name = _normalize_header(name)
        self._combined_cache[norm_name] = value
        self._as_list[norm_name] = [value]</search>
<replace>
        norm_name = _to_header_case(name)
        self._combined_cache[norm_name] = value
        self._as_list[norm_name] = [value]</replace>
</edit>
<edit file="tornado/httputil.py">
<search>
        norm_name = _normalize_header(name)
        return norm_name in self._as_list</search>
<replace>
        norm_name = _to_header_case(name)
        return norm_name in self._as_list</replace>
</edit>
<edit file="tornado/httputil.py">
<search>
        header = _normalize_header(name)
        if header not in self._combined_cache:</search>
<replace>
        header = _to_header_case(name)
        if header not in self._combined_cache:</replace>
</edit>
<edit file="tornado/httputil.py">
<search>
        norm_name = _normalize_header(name)
        # _combined_cache is populated lazily by __getitem__ and invalidated</search>
<replace>
        norm_name = _to_header_case(name)
        # _combined_cache is populated lazily by __getitem__ and invalidated</replace>
</edit>

<riesgos>
Solo se me proporcionaron archivos de `tornado/`; no vi el directorio `tornado/test` ni otros archivos como `docs`. Si alguno importa o usa `_normalize_header` (por ejemplo `tornado/test/httputil_test.py`), habría que actualizarlo también.
</riesgos>