Extraigo el bloque `try`/`except` de `_parse_request_range` a una función nueva `_parse_range_bounds`. Esta devuelve `(start, end)`, o `None` si algún valor no es un entero válido. En `_parse_request_range` la llamada conserva el `return None` en ese caso.

<edit file="tornado/httputil.py">
<search>
    start_b, _, end_b = value.partition("-")
    try:
        start = _int_or_none(start_b)
        end = _int_or_none(end_b)
    except ValueError:
        return None
    if end is not None:
        if start is None:
            if end != 0:</search>
<replace>
    start_b, _, end_b = value.partition("-")
    bounds = _parse_range_bounds(start_b, end_b)
    if bounds is None:
        return None
    start, end = bounds
    if end is not None:
        if start is None:
            if end != 0:</replace>
</edit>

<edit file="tornado/httputil.py">
<search>
def _get_content_range(start: int | None, end: int | None, total: int) -> str:</search>
<replace>
def _parse_range_bounds(
    start_b: str, end_b: str
) -> tuple[int | None, int | None] | None:
    try:
        start = _int_or_none(start_b)
        end = _int_or_none(end_b)
    except ValueError:
        return None
    return start, end


def _get_content_range(start: int | None, end: int | None, total: int) -> str:</replace>
</edit>

<riesgos>
ninguno
</riesgos>