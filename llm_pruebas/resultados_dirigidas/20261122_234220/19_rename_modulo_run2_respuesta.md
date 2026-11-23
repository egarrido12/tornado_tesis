Renombro `tornado/locks.py` a `tornado/sync.py` y actualizo todas las referencias que aparecen en el contexto:

- **`tornado/__init__.py`:** sustituyo `"locks"` por `"sync"` en `__all__`, en orden alfabético.
- **`tornado/queues.py` y los tests:** cambio los imports `from tornado.locks import ...` por `from tornado.sync import ...`.
- **`locks_test.py`:** importo con `from tornado import gen, sync as locks` para no tocar todos los usos. Mantengo el nombre del archivo de test.
- **Docstrings de `locks.py`:** actualizo los ejemplos que importan `tornado.locks`.
- **`tornado/test/api.txt`:** muevo la sección `[tornado.locks]` a `[tornado.sync]`, colocada entre `simple_httpclient` y `tcpclient` para mantener el orden alfabético.

<edit file="tornado/__init__.py">
<search>
    "locks",
</search>
<replace>
</replace>
</edit>
<edit file="tornado/__init__.py">
<search>
    "simple_httpclient",
    "tcpclient",
</search>
<replace>
    "simple_httpclient",
    "sync",
    "tcpclient",
</replace>
</edit>
<edit file="tornado/queues.py">
<search>
from tornado.locks import Event
</search>
<replace>
from tornado.sync import Event
</replace>
</edit>
<edit file="tornado/locks.py">
<search>
        from tornado.locks import Condition
</search>
<replace>
        from tornado.sync import Condition
</replace>
</edit>
<edit file="tornado/locks.py">
<search>
        from tornado.locks import Event
</search>
<replace>
        from tornado.sync import Event
</replace>
</edit>
<edit file="tornado/locks.py">
<search>
        from tornado.locks import Semaphore
</search>
<replace>
        from tornado.sync import Semaphore
</replace>
</edit>
<edit file="tornado/locks.py">
<search>
    >>> from tornado import locks
    >>> lock = locks.Lock()
</search>
<replace>
    >>> from tornado import sync
    >>> lock = sync.Lock()
</replace>
</edit>
<edit file="tornado/test/locks_test.py">
<search>
from tornado import gen, locks
</search>
<replace>
from tornado import gen, sync as locks
</replace>
</edit>
<edit file="tornado/test/httpclient_test.py">
<search>
from tornado.locks import Event
</search>
<replace>
from tornado.sync import Event
</replace>
</edit>
<edit file="tornado/test/httpserver_test.py">
<search>
from tornado.locks import Event
</search>
<replace>
from tornado.sync import Event
</replace>
</edit>
<edit file="tornado/test/simple_httpclient_test.py">
<search>
from tornado.locks import Event
</search>
<replace>
from tornado.sync import Event
</replace>
</edit>
<edit file="tornado/test/testing_test.py">
<search>
from tornado.locks import Event
</search>
<replace>
from tornado.sync import Event
</replace>
</edit>
<edit file="tornado/test/web_test.py">
<search>
from tornado.locks import Event
</search>
<replace>
from tornado.sync import Event
</replace>
</edit>
<edit file="tornado/test/http1connection_test.py">
<search>
from tornado.locks import Event
</search>
<replace>
from tornado.sync import Event
</replace>
</edit>
<edit file="tornado/test/iostream_test.py">
<search>
from tornado.locks import Condition, Event
</search>
<replace>
from tornado.sync import Condition, Event
</replace>
</edit>
<edit file="tornado/test/websocket_test.py">
<search>
from tornado.locks import Event
</search>
<replace>
from tornado.sync import Event
</replace>
</edit>
<edit file="tornado/test/api.txt">
<search>
[tornado.locks]
tornado.locks.BoundedSemaphore: class(tornado.locks.Semaphore)
tornado.locks.BoundedSemaphore.__init__: method(self, value=1)
tornado.locks.BoundedSemaphore.release: method(self)
tornado.locks.Condition: class(tornado.locks._TimeoutGarbageCollector)
tornado.locks.Condition.__init__: method(self)
tornado.locks.Condition.__repr__: method(self)
tornado.locks.Condition.notify: method(self, n=1)
tornado.locks.Condition.notify_all: method(self)
tornado.locks.Condition.wait: method(self, timeout=None)
tornado.locks.Event: class()
tornado.locks.Event.__init__: method(self)
tornado.locks.Event.__repr__: method(self)
tornado.locks.Event.clear: method(self)
tornado.locks.Event.is_set: method(self)
tornado.locks.Event.set: method(self)
tornado.locks.Event.wait: method(self, timeout=None)
tornado.locks.Lock: class()
tornado.locks.Lock.__aenter__: method(self)
tornado.locks.Lock.__aexit__: method(self, typ, value, tb)
tornado.locks.Lock.__enter__: method(self)
tornado.locks.Lock.__exit__: method(self, typ, value, tb)
tornado.locks.Lock.__init__: method(self)
tornado.locks.Lock.__repr__: method(self)
tornado.locks.Lock.acquire: method(self, timeout=None)
tornado.locks.Lock.release: method(self)
tornado.locks.Semaphore: class(tornado.locks._TimeoutGarbageCollector)
tornado.locks.Semaphore.__aenter__: method(self)
tornado.locks.Semaphore.__aexit__: method(self, typ, value, tb)
tornado.locks.Semaphore.__enter__: method(self)
tornado.locks.Semaphore.__exit__: method(self, typ, value, traceback)
tornado.locks.Semaphore.__init__: method(self, value=1)
tornado.locks.Semaphore.__repr__: method(self)
tornado.locks.Semaphore.acquire: method(self, timeout=None)
tornado.locks.Semaphore.release: method(self)

[tornado.log]
</search>
<replace>
[tornado.log]
</replace>
</edit>
<edit file="tornado/test/api.txt">
<search>
[tornado.tcpclient]
</search>
<replace>
[tornado.sync]
tornado.sync.BoundedSemaphore: class(tornado.sync.Semaphore)
tornado.sync.BoundedSemaphore.__init__: method(self, value=1)
tornado.sync.BoundedSemaphore.release: method(self)
tornado.sync.Condition: class(tornado.sync._TimeoutGarbageCollector)
tornado.sync.Condition.__init__: method(self)
tornado.sync.Condition.__repr__: method(self)
tornado.sync.Condition.notify: method(self, n=1)
tornado.sync.Condition.notify_all: method(self)
tornado.sync.Condition.wait: method(self, timeout=None)
tornado.sync.Event: class()
tornado.sync.Event.__init__: method(self)
tornado.sync.Event.__repr__: method(self)
tornado.sync.Event.clear: method(self)
tornado.sync.Event.is_set: method(self)
tornado.sync.Event.set: method(self)
tornado.sync.Event.wait: method(self, timeout=None)
tornado.sync.Lock: class()
tornado.sync.Lock.__aenter__: method(self)
tornado.sync.Lock.__aexit__: method(self, typ, value, tb)
tornado.sync.Lock.__enter__: method(self)
tornado.sync.Lock.__exit__: method(self, typ, value, tb)
tornado.sync.Lock.__init__: method(self)
tornado.sync.Lock.__repr__: method(self)
tornado.sync.Lock.acquire: method(self, timeout=None)
tornado.sync.Lock.release: method(self)
tornado.sync.Semaphore: class(tornado.sync._TimeoutGarbageCollector)
tornado.sync.Semaphore.__aenter__: method(self)
tornado.sync.Semaphore.__aexit__: method(self, typ, value, tb)
tornado.sync.Semaphore.__enter__: method(self)
tornado.sync.Semaphore.__exit__: method(self, typ, value, traceback)
tornado.sync.Semaphore.__init__: method(self, value=1)
tornado.sync.Semaphore.__repr__: method(self)
tornado.sync.Semaphore.acquire: method(self, timeout=None)
tornado.sync.Semaphore.release: method(self)

[tornado.tcpclient]
</replace>
</edit>
<rename_file from="tornado/locks.py" to="tornado/sync.py"/>

<riesgos>
No pude ver archivos fuera del contexto: la documentación (`docs/locks.rst`, `docs/index.rst`, etc.), `runtests.py`, que lista los módulos de test, y otros usos de `tornado.locks`. Esas referencias, si existen, siguen apuntando al nombre antiguo. El módulo `tornado.locks` deja de existir sin alias de compatibilidad, así que el código externo que lo importe dejará de funcionar. Tampoco pude confirmar que `api.txt` admita el nuevo orden de secciones.
</riesgos>