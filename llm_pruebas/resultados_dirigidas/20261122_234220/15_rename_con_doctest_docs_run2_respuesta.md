Renombro `_normalize_header` a `_to_header_case` en `tornado/httputil.py`, que es el único archivo del contexto que lo menciona. Los cambios son la definición, el doctest de su docstring y los seis usos dentro de `HTTPHeaders`.

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
No se proporcionaron los archivos de pruebas (p. ej. tornado/test/*) ni la documentación, por lo que no pude verificar si alguno importa `_normalize_header`. Conviene buscarlo con grep en todo el repositorio.
</riesgos>