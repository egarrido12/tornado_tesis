Extraigo las dos líneas que parten el encabezado (`partition` y `strip`) a `_split_range_header`, que devuelve `(unit, value)`, y las sustituyo por una llamada en `_parse_request_range`. Coloco la función nueva justo antes de `_parse_request_range`.

<edit file="tornado/httputil.py">
<search>
def _parse_request_range(
    range_header: str,
) -> tuple[int | None, int | None] | None:
    """Parses a Range header.</search>
<replace>
def _split_range_header(range_header: str) -> tuple[str, str]:
    """Splits a Range header into its unit and value (both stripped)."""
    unit, _, value = range_header.partition("=")
    unit, value = unit.strip(), value.strip()
    return unit, value


def _parse_request_range(
    range_header: str,
) -> tuple[int | None, int | None] | None:
    """Parses a Range header.</replace>
</edit>

<edit file="tornado/httputil.py">
    unit, _, value = range_header.partition("=")
    unit, value = unit.strip(), value.strip()
    if unit != "bytes":
        return None
    start_b, _, end_b = value.partition("-")</search>
<replace>    unit, value = _split_range_header(range_header)
    if unit != "bytes":
        return None
    start_b, _, end_b = value.partition("-")</replace>
</edit>

<riesgos>
ninguno
</riesgos>