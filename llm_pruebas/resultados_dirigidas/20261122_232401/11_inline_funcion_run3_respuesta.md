`_int_or_none` solo se usa en `_parse_request_range`, con dos llamadas. Hay que comprobar que no se use en otros archivos: en el contexto proporcionado no aparece en ningún otro módulo.

El cuerpo de la función es:
```python
val = val.strip()
if val == "":
    return None
return int(val)
```

Para preservar el comportamiento (incluido `ValueError` dentro del `try`), sustituyo cada llamada por una expresión condicional equivalente: `None if start_b.strip() == "" else int(start_b.strip())`. El `strip()` se evalúa en la misma posición que antes y `int()` sigue lanzando `ValueError` dentro del `try`.

<edit file="tornado/httputil.py">
<search>
        start = _int_or_none(start_b)
        end = _int_or_none(end_b)
</search>
<replace>
        start = None if start_b.strip() == "" else int(start_b.strip())
        end = None if end_b.strip() == "" else int(end_b.strip())
</replace>
</edit>

<edit file="tornado/httputil.py">
<search>
def _int_or_none(val: str) -> int | None:
    val = val.strip()
    if val == "":
        return None
    return int(val)


@dataclasses.dataclass
class ParseMultipartConfig:
</search>
<replace>
@dataclasses.dataclass
class ParseMultipartConfig:
</replace>
</edit>

<riesgos>
Solo he verificado los usos de `_int_or_none` en los archivos del contexto; si algún archivo de pruebas o externo la importa, fallaría.
</riesgos>