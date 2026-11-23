Renombro `HelloHandler.get` a `handle_get` en `tornado/test/web_test.py` y añado el alias `get = handle_get`. Tornado despacha las peticiones GET buscando el método `get` por nombre, así que sin el alias `HandlerByNameTest` dejaría de funcionar.

Las otras clases `HelloHandler` (en `httpserver_test.py` e `iostream_test.py`) son distintas y no las toco. No hay llamadas directas a `HelloHandler.get` en el proyecto.

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

    # RequestHandler dispatches GET requests to the method named ``get``.
    get = handle_get
</replace>
</edit>

<riesgos>
Un renombrado literal sin alias rompería el despacho HTTP de Tornado (el método `get` se busca por nombre), por eso se mantiene `get = handle_get`. No he podido ejecutar la suite; no hay otras referencias a `HelloHandler.get` en el contexto recibido.
</riesgos>