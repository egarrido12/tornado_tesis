Renombro `doctests` a `doctest_suite` solo en `tornado/httputil.py`. Las funciones `doctests` de `iostream` y `util` no se tocan. Actualizo las dos referencias que aparecen en el contexto: `TEST_MODULES` en `runtests.py` y el snapshot de la API en `api.txt`.

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
No pude revisar archivos que no están en el contexto (docs, otros tests, `.rst`). Si alguno menciona `tornado.httputil.doctests`, hay que actualizarlo.
</riesgos>