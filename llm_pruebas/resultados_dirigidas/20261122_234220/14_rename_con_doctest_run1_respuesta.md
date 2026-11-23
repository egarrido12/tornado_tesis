Busco todas las referencias a `_normalize_header` en los archivos recibidos. Todas están en `tornado/httputil.py`: la definición, el docstring (que incluye un doctest) y los usos dentro de `HTTPHeaders`. En el resto de los archivos mostrados no aparece.

Cada bloque `<search>` incluye contexto para que aparezca una sola vez en el archivo.

<edit file="tornado/httputil.py">
<search>
def _normalize_header(name: str) -> str:
    """Map a header name to Http-Header-Case.

    >>> _normalize_header("coNtent-TYPE")</search>
<replace>
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
        # _combined_cache is populated lazily</search>
<replace>
        norm_name = _to_header_case(name)
        # _combined_cache is populated lazily</replace>
</edit>

<riesgos>
Solo pude revisar los archivos del contexto; los tests en `tornado/test/` no se me mostraron. Si alguno importa `_normalize_header` de `httputil`, habrá que actualizarlo. Quedaría fuera de este cambio.
</riesgos>