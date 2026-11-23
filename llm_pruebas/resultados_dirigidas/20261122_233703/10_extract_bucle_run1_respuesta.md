Extraigo el bucle de fusión de argumentos urlencoded a una función de módulo `_merge_urlencoded_arguments` y la llamo desde `parse_body_arguments`. Defino la función justo antes de `parse_body_arguments`, y la llamada sustituye al bucle original sin cambiar la lógica.

<edit file="tornado/httputil.py">
<search>
def parse_body_arguments(
    content_type: str,</search>
<replace>
def _merge_urlencoded_arguments(
    uri_arguments: dict[str, list[bytes]], arguments: dict[str, list[bytes]]
) -> None:
    for name, values in uri_arguments.items():
        if values:
            arguments.setdefault(name, []).extend(values)


def parse_body_arguments(
    content_type: str,</replace>
</edit>
<edit file="tornado/httputil.py">
<search>
        for name, values in uri_arguments.items():
            if values:
                arguments.setdefault(name, []).extend(values)
    elif content_type.startswith("multipart/form-data"):</search>
<replace>
        _merge_urlencoded_arguments(uri_arguments, arguments)
    elif content_type.startswith("multipart/form-data"):</replace>
</edit>

<riesgos>
ninguno
</riesgos>