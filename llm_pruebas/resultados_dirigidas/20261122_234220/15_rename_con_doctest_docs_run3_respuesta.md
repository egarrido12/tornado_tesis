Solo `tornado/httputil.py` usa `_normalize_header`: la definición, el doctest de su docstring y seis usos dentro de `HTTPHeaders`. Ningún otro archivo del contexto lo referencia. Hago un bloque `<edit>` por cada ocurrencia.

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
No pude ver los archivos de tests ni otros módulos fuera del contexto (p. ej. `tornado/test/*`, docs); si alguno referencia `_normalize_header` habría que actualizarlo.
</riesgos>