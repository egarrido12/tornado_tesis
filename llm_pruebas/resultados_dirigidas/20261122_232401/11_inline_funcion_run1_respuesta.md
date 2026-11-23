`_int_or_none` solo se usa en `_parse_request_range` (dos llamadas dentro de un `try`). Hay que comprobar que no se use en otros archivos: en el código recibido no aparece en ningún otro sitio.

Cuerpo de la función:
```python
val = val.strip()
if val == "":
    return None
return int(val)
```

Para hacer el inline sin cambiar el comportamiento, sustituyo cada llamada por una expresión equivalente: `(None if start_b.strip() == "" else int(start_b.strip()))`. `int()` ya ignora los espacios, pero conservo el `strip()` para que el cuerpo sea idéntico. Los `ValueError` de `int` siguen cayendo en el mismo `try`/`except`.

<edit file="tornado/httputil.py">
<search>
    try:
        start = _int_or_none(start_b)
        end = _int_or_none(end_b)
    except ValueError:
</search>
<replace>
    try:
        start = None if start_b.strip() == "" else int(start_b.strip())
        end = None if end_b.strip() == "" else int(end_b.strip())
    except ValueError:
</replace>
</edit>

<edit file="tornado/httputil.py">
<search>
def _int_or_none(val: str) -> int | None:
    val = val.strip()
    if val == "":
        return None
    return int(val)


</search>
<replace>
</replace>
</edit>

<riesgos>
No se pudo buscar el uso de `_int_or_none` en archivos fuera del contexto (por ejemplo, tests de `tornado/test`); si algún test lo importa, fallaría.
</riesgos>