Renombro `doctests` a `doctest_suite` en `tornado/httputil.py` y actualizo las dos referencias que aparecen en el contexto: la lista `TEST_MODULES` de `runtests.py` y la instantánea de la API (`api.txt`). Las funciones `doctests` de `iostream` y `util` no se tocan.

<edit file="tornado/httputil.py">
<search>
def doctests() -> unittest.TestSuite:
</search>
<replace>
def doctest_suite() -> unittest.TestSuite:
</replace>
</edit>

<edit file="tornado/test/runtests.py">
<search>
    "tornado.httputil.doctests",
</search>
<replace>
    "tornado.httputil.doctest_suite",
</replace>
</edit>

<edit file="tornado/test/api.txt">
<search>
tornado.httputil.doctests: function()
</search>
<replace>
tornado.httputil.doctest_suite: function()
</replace>
</edit>

<riesgos>
No pude revisar archivos fuera del contexto (documentación `docs/*.rst`, `conf.py`, otros tests) que pudieran referirse a `tornado.httputil.doctests`; conviene buscarlo con grep. Si esa función estuviera listada en la lista de ignorados de `docs/conf.py`, habría que actualizarla también.
</riesgos>