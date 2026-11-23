Referencias a `_maybe_add_error_listener` en `tornado/iostream.py`:

1. En `write`: `self._maybe_add_error_listener()` (tras `_add_io_state(self.io_loop.WRITE)`).
2. En `set_close_callback`: `self._maybe_add_error_listener()`.
3. En `_finish_read`: `self._maybe_add_error_listener()`.
4. La definición `def _maybe_add_error_listener(self)`.

Los tests mostrados no la mencionan por nombre. Ningún otro archivo del paquete la usa. Cada bloque `<search>` incluye contexto para que aparezca una sola vez.

<edit file="tornado/iostream.py">
<search>
            if self._write_buffer:
                self._add_io_state(self.io_loop.WRITE)
            self._maybe_add_error_listener()
        return future
</search>
<replace>
            if self._write_buffer:
                self._add_io_state(self.io_loop.WRITE)
            self._ensure_error_listener()
        return future
</replace>
</edit>

<edit file="tornado/iostream.py">
<search>
        self._close_callback = callback
        self._maybe_add_error_listener()

    def close(
</search>
<replace>
        self._close_callback = callback
        self._ensure_error_listener()

    def close(
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

<riesgos>
No pude verificar referencias fuera de los archivos mostrados (otros tests o código externo que use el nombre privado `_maybe_add_error_listener`, p. ej. mediante mocks o subclases). En los archivos recibidos no hay más usos, ni siquiera en los comentarios.
</riesgos>