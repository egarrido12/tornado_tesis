Renombro `HelloHandler.get` a `handle_get` y añado el alias `get = handle_get` en la misma clase. `RequestHandler` despacha las peticiones GET con `getattr(self, "get")`, así que sin el alias `HandlerByNameTest` recibiría 405 en lugar de "hello". No hay otras referencias a `HelloHandler.get` en el proyecto. El `HelloHandler` de `iostream_test.py` es otra clase y no se toca.

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
El alias `get = handle_get` es necesario por el despacho de `RequestHandler`; sin él cambiaría el comportamiento. No hay otras referencias a `HelloHandler.get` en el contexto recibido, pero no he podido revisar archivos que no aparezcan en él.
</riesgos>