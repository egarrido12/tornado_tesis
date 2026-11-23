Extraigo las dos líneas que separan la unidad y el valor (`partition` y `strip`) a `_split_range_header`, que devuelve la tupla `(unit, value)`. En `_parse_request_range` las sustituyo por una única llamada.

<edit file="tornado/httputil.py">
<search>
    unit, _, value = range_header.partition("=")
    unit, value = unit.strip(), value.strip()
    if unit != "bytes":
        return None
</search>
<replace>
    unit, value = _split_range_header(range_header)
    if unit != "bytes":
        return None
</replace>
</edit>
<edit file="tornado/httputil.py">
<search>
def _parse_request_range(
    range_header: str,
) -> tuple[int | None, int | None] | None:
</search>
<replace>
def _split_range_header(range_header: str) -> tuple[str, str]:
    """Splits a Range header into its (stripped) unit and value."""
    unit, _, value = range_header.partition("=")
    unit, value = unit.strip(), value.strip()
    return unit, value


def _parse_request_range(
    range_header: str,
) -> tuple[int | None, int | None] | None:
</replace>
</edit>

<riesgos>
ninguno
</riesgos>