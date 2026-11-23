Renombro `BaseIOStream._maybe_add_error_listener` a `_ensure_error_listener` en `tornado/iostream.py`: la definición y sus tres llamadas (en `write`, `set_close_callback` y `_finish_read`). También actualizo el comentario de `tornado/test/iostream_test.py` que menciona el nombre antiguo.

<edit file="tornado/iostream.py">
<search>
                self._add_io_state(self.io_loop.WRITE)
            self._maybe_add_error_listener()
</search>
<replace>
                self._add_io_state(self.io_loop.WRITE)
            self._ensure_error_listener()
</replace>
</edit>

<edit file="tornado/iostream.py">
<search>
        self._close_callback = callback
        self._maybe_add_error_listener()
</search>
<replace>
        self._close_callback = callback
        self._ensure_error_listener()
</replace>
</edit>

<edit file="tornado/iostream.py">
<search>
            future_set_result_unless_cancelled(future, result)
        self._maybe_add_error_listener()
</search>
<replace>
            future_set_result_unless_cancelled(future, result)
        self._ensure_error_listener()
</replace>
</edit>

<edit file="tornado/iostream.py">
<search>
    def _maybe_add_error_listener(self) -> None:
</search>
<replace>
    def _ensure_error_listener(self) -> None:
</replace>
</edit>

<edit file="tornado/test/iostream_test.py">
<search>
        # and IOStream._maybe_add_error_listener.
</search>
<replace>
        # and IOStream._ensure_error_listener.
</replace>
</edit>

<riesgos>
Solo he podido revisar los archivos que aparecen en el contexto. No he podido comprobar si otros módulos o pruebas del proyecto que no se muestran (por ejemplo, subclases fuera de `tornado/`) usan el nombre antiguo.
</riesgos>