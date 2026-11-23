`_int_or_none` solo se usa en `_parse_request_range`, con dos llamadas. Hago inline del cuerpo en cada una y elimino la definición.

El cuerpo es:
```python
val = val.strip()
if val == "":
    return None
return int(val)
```

Las llamadas están dentro de un `try` que captura `ValueError`, así que mantengo `int(...)` dentro del `try`. Para conservar el comportamiento, `int(x.strip())` ya acepta cadenas con espacios, pero la cadena vacía debe dar `None`, no un error. Por eso uso una expresión condicional.

Solo toco `tornado/httputil.py`. No he buscado usos de `_int_or_none` en otros archivos del paquete ni en las pruebas.

<edit file="tornado/httputil.py">
<search>
    try:
        start = _int_or_none(start_b)
        end = _int_or_none(end_b)
    except ValueError:
        return None
</search>
<replace>
    try:
        start_b = start_b.strip()
        start = None if start_b == "" else int(start_b)
        end_b = end_b.strip()
        end = None if end_b == "" else int(end_b)
    except ValueError:
        return None
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
No he verificado que `_int_or_none` no se use en otros módulos o en las pruebas (solo vi el código mostrado, donde no aparece fuera de `httputil.py`). Si algún test la importa, fallaría.
</riesgos>