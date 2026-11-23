Extraigo el bloque `try`/`except` a `_parse_range_bounds`, que devuelve `None` si hay `ValueError` y `(start, end)` en caso contrario. En `_parse_request_range` desempaqueto el resultado, conservando el `return None` anterior.

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
            if end != 0:
                start = -end
                end = None
        else:
            end += 1
    return (start, end)
</search>
<replace>
    start_b, _, end_b = value.partition("-")
    bounds = _parse_range_bounds(start_b, end_b)
    if bounds is None:
        return None
    start, end = bounds
    if end is not None:
        if start is None:
            if end != 0:
                start = -end
                end = None
        else:
            end += 1
    return (start, end)


def _parse_range_bounds(
    start_b: str, end_b: str
) -> tuple[int | None, int | None] | None:
    try:
        start = _int_or_none(start_b)
        end = _int_or_none(end_b)
    except ValueError:
        return None
    return (start, end)
</replace>
</edit>

<riesgos>
ninguno
</riesgos>