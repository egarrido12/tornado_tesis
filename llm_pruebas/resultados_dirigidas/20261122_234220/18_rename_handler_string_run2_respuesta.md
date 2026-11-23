Renombro `HelloHandler` a `GreetingHandler` solo en `tornado/test/web_test.py`, donde se define. Allí cambio la definición de la clase, su uso directo en `HandlerByNameTest` y las dos referencias por nombre completo `"tornado.test.web_test.HelloHandler"`. Los otros archivos de prueba (`iostream_test.py` y `httpserver_test.py`) tienen su propio `HelloHandler` independiente, así que no los toco.

<edit file="tornado/test/web_test.py">
<search>
class HelloHandler(RequestHandler):
</search>
<replace>
class GreetingHandler(RequestHandler):
</replace>
</edit>
<edit file="tornado/test/web_test.py">
<search>
            ("/hello1", HelloHandler),
            ("/hello2", "tornado.test.web_test.HelloHandler"),
            url("/hello3", "tornado.test.web_test.HelloHandler"),
</search>
<replace>
            ("/hello1", GreetingHandler),
            ("/hello2", "tornado.test.web_test.GreetingHandler"),
            url("/hello3", "tornado.test.web_test.GreetingHandler"),
</replace>
</edit>

<riesgos>
Solo he podido revisar los archivos que me pasaste; si otro módulo importa `HelloHandler` desde `tornado.test.web_test`, no lo habría visto.
</riesgos>