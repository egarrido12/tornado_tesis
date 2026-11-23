Extraigo el bloque que quita las comillas del boundary a una función de módulo `_unquote_boundary`, definida justo antes de `parse_multipart_form_data`. En `parse_multipart_form_data` lo sustituyo por una llamada a esa función. El comentario explicativo se queda donde estaba, junto a la llamada.

<edit file="tornado/httputil.py">
<search>
def parse_multipart_form_data(
    boundary: bytes,
    data: bytes,
    arguments: dict[str, list[bytes]],
    files: dict[str, list[HTTPFile]],
    *,
    config: ParseMultipartConfig | None = None,
) -> None:
</search>
<replace>
def _unquote_boundary(boundary: bytes) -> bytes:
    if boundary.startswith(b'"') and boundary.endswith(b'"'):
        boundary = boundary[1:-1]
    return boundary


def parse_multipart_form_data(
    boundary: bytes,
    data: bytes,
    arguments: dict[str, list[bytes]],
    files: dict[str, list[HTTPFile]],
    *,
    config: ParseMultipartConfig | None = None,
) -> None:
</replace>
</edit>
<edit file="tornado/httputil.py">
<search>
    if boundary.startswith(b'"') and boundary.endswith(b'"'):
        boundary = boundary[1:-1]
    final_boundary_index = data.rfind(b"--" + boundary + b"--")
</search>
<replace>
    boundary = _unquote_boundary(boundary)
    final_boundary_index = data.rfind(b"--" + boundary + b"--")
</replace>
</edit>

<riesgos>
ninguno
</riesgos>