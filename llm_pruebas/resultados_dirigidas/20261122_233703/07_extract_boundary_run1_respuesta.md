Extraigo el bloque que quita las comillas del boundary a una función de módulo `_unquote_boundary`, definida justo antes de `parse_multipart_form_data`. El comentario explicativo se queda en la función nueva y el bloque original pasa a ser una llamada.

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
    # The standard allows for the boundary to be quoted in the header,
    # although it's rare (it happens at least for google app engine
    # xmpp).  I think we're also supposed to handle backslash-escapes
    # here but I'll save that until we see a client that uses them
    # in the wild.
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
    # The standard allows for the boundary to be quoted in the header,
    # although it's rare (it happens at least for google app engine
    # xmpp).  I think we're also supposed to handle backslash-escapes
    # here but I'll save that until we see a client that uses them
    # in the wild.
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