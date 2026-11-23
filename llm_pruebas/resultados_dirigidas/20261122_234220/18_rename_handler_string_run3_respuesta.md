Renombro `HelloHandler` a `GreetingHandler` en `tornado/test/web_test.py`: la definición de la clase y las tres referencias en `HandlerByNameTest`, una directa y dos por nombre calificado como cadena. Los `HelloHandler` de `httpserver_test.py` e `iostream_test.py` son clases locales distintas, así que no los toco.

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
Solo he revisado los archivos del contexto; si otro módulo importa `HelloHandler` desde `tornado.test.web_test`, no lo he podido ver.
</riesgos>