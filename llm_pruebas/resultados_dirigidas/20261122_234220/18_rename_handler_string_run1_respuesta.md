Renombro `HelloHandler` a `GreetingHandler` solo en `tornado/test/web_test.py`: la definición de la clase y sus referencias en `HandlerByNameTest`, incluidas las dos cadenas `"tornado.test.web_test.HelloHandler"`, que se importan por nombre. Las clases `HelloHandler` de `iostream_test.py` y `httpserver_test.py` son otras distintas y no las toco.

<edit file="tornado/test/web_test.py">
<search>
class HelloHandler(RequestHandler):
    def get(self):
        self.write("hello")
</search>
<replace>
class GreetingHandler(RequestHandler):
    def get(self):
        self.write("hello")
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
Las clases `HelloHandler` de `tornado/test/iostream_test.py` y `tornado/test/httpserver_test.py` (esta última es una clase interna de otra función) son independientes y no se han modificado. No he podido comprobar si algún otro archivo, como documentación, importa `tornado.test.web_test.HelloHandler`.
</riesgos>