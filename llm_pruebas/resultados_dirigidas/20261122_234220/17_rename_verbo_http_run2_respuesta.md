Renombro `HelloHandler.get` a `handle_get` en `tornado/test/web_test.py` y dejo `get = handle_get` para que `RequestHandler` siga encontrándolo, ya que lo busca por nombre con `getattr(self, request.method.lower())`.

Sin ese alias, `HandlerByNameTest` dejaría de pasar. Es lo único que se puede hacer sin cambiar el comportamiento.

No hay referencias directas a `HelloHandler.get` en el resto del proyecto. Las otras clases llamadas `HelloHandler` (por ejemplo en `iostream_test.py`) son distintas y no las toco.

<edit file="tornado/test/web_test.py">
<search>
class HelloHandler(RequestHandler):
    def get(self):
        self.write("hello")
</search>
<replace>
class HelloHandler(RequestHandler):
    def handle_get(self):
        self.write("hello")

    get = handle_get
</replace>
</edit>

<riesgos>
Se añadió el alias `get = handle_get` porque el despacho de `RequestHandler` es dinámico (`getattr(self, "get")`); sin él fallaría `HandlerByNameTest`. No hay otras referencias directas a `HelloHandler.get` en el proyecto.
</riesgos>