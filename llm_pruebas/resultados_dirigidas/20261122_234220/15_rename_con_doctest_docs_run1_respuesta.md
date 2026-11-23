Renombro `_normalize_header` a `_to_header_case` en `tornado/httputil.py`: la definición, el doctest de su docstring y los seis usos dentro de `HTTPHeaders` (`add`, `get_list`, `__setitem__`, `__contains__`, `__getitem__`, `__delitem__`). En los archivos que recibí no aparece ninguna otra referencia a ese nombre.

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
</search>
<replace>
        norm_name = _to_header_case(name)
        if norm_name in self:
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
No pude ver los archivos de pruebas (por ejemplo `tornado/test/*`) ni la documentación. Si alguno importa o menciona `_normalize_header`, quedará sin actualizar.
</riesgos>