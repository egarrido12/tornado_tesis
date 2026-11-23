Extraigo el bucle a una función de módulo `_merge_urlencoded_arguments(uri_arguments, arguments)` y lo sustituyo por una llamada en `parse_body_arguments`. La función nueva va justo antes de `parse_body_arguments`.

<edit file="tornado/httputil.py">
<search>
def parse_body_arguments(
    content_type: str,</search>
<replace>
def _merge_urlencoded_arguments(
    uri_arguments: dict[str, list[bytes]],
    arguments: dict[str, list[bytes]],
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