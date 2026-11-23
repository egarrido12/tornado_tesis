Renombro `doctests` a `doctest_suite` en `tornado/httputil.py` y actualizo las dos referencias externas: la lista `TEST_MODULES` de `runtests.py` y el snapshot `api.txt`. Dejo intactas las funciones `doctests` de `iostream` y `util`, porque son otras definiciones.

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
No pude buscar en archivos que no se me mostraron, como docs o tests no incluidos. Si algún otro archivo referencia `tornado.httputil.doctests`, no queda actualizado.
</riesgos>