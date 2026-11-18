# Pruebas de Tornado con Rope (+ huella de carbono con CodeCarbon)

Este documento describe el proceso completo: qué se probó, cómo reproducirlo, qué resultados se obtuvieron y cómo interpretarlos. Es una réplica del experimento hecho sobre PySnooper (`../PySnooper_tesis/rope_pruebas/`) y Cookiecutter (`../cookiecutter_tesis/rope_pruebas/`), con la misma metodología y los mismos tipos de refactorización. **La novedad** es que cada fase se mide con [CodeCarbon](https://codecarbon.io) para estimar la energía y las emisiones de CO2 de usar Rope.

- **Proyecto bajo prueba:** Tornado 6.7.dev1 (commit `57deb98e`), carpeta `tornado/` (25 996 líneas en 35 módulos, incluido `tornado/platform/`).
- **Herramienta:** [Rope](https://github.com/python-rope/rope) 1.15.0, una biblioteca de refactorización automática para Python.
- **Medición de carbono:** [CodeCarbon](https://codecarbon.io) 3.3.2, modo offline.
- **Entorno:** Python 3.12.15 (instalado con `uv`), macOS 15.6.1 (Darwin 24.6.0), Apple M4, 16 GB de RAM.
- **Fecha de ejecución:** 2026-10-30.

> **Diferencias de entorno con los experimentos anteriores:**
> - Tornado requiere Python ≥ 3.11, así que, igual que en Cookiecutter, se usó Python 3.12 y no el 3.9.6 del sistema.
> - Tornado **no usa pytest**: su suite oficial es `unittest` y se corre con `python -m tornado.test.runtests`.
> - Tornado **no debe estar instalado** en el `.venv` (ver sección 2.1). Esto es distinto de Cookiecutter, donde sí estaba instalado en modo editable.

---

## 1. Objetivo y metodología

Hay dos preguntas:

1. **¿Las refactorizaciones automáticas de Rope conservan el comportamiento de Tornado?**
2. **¿Cuál es la huella de carbono de usar Rope?** Es decir, cuánta energía y cuántas emisiones produce cada operación de Rope y cuánto cuesta verificarla con los tests.

La suite de tests de Tornado sirve como oráculo:

1. **Reposo:** CodeCarbon mide el equipo 20 s sin hacer nada. Es la referencia del ruido de fondo.
2. **Línea base:** se corre la suite original **3 veces** y se anota el resultado de referencia y la variabilidad del consumo.
3. **Análisis estático:** se usan las herramientas de análisis de Rope (`find_errors`, `find_occurrences`, `find_definition`) sin modificar código.
4. **Refactorizaciones:** cada refactorización se aplica con la API de Rope **sobre una copia limpia e independiente** del proyecto. La operación de Rope se repite **5 veces** (cada vez sobre una copia nueva) para medir su consumo con media y desviación estándar. Se guarda el diff y se vuelve a correr la suite completa.
5. **Veredicto:** si el número de tests que pasan es igual al de la línea base y no hay fallos ni errores, la refactorización **preserva el comportamiento**. Si no, **rompe tests**. Si Rope se niega a aplicarla, queda como **rechazada por Rope**.

Las refactorizaciones **02 a 12 reproducen una por una los tipos probados en PySnooper y Cookiecutter**, con la misma numeración: 5 Rename, 4 Extract Method, 1 Inline y 1 Move. Las **13 a 20 son casos nuevos** que aparecen por características de Tornado:

| Característica de Tornado | Caso |
|---|---|
| Tests que parchean métodos con `mock.patch("tornado.iostream.BaseIOStream._try_inline_read")` | 13 |
| Doctests dentro de los docstrings, que se ejecutan como parte de la suite | 14, 15 |
| La lista `TEST_MODULES` del runner nombra tests como strings (`"tornado.httputil.doctests"`) | 16 |
| `RequestHandler` despacha la petición con `getattr(self, método_http.lower())` | 17 |
| Las rutas pueden nombrar el handler como string (`"tornado.test.web_test.HelloHandler"`) | 18 |
| `tornado/__init__.py` lista los submódulos como strings en `__all__` (import perezoso, PEP 562) | 19 |
| Código asíncrono (`async def` / `await`) | 20 |

Son la versión Tornado de lo que en PySnooper era `.format(**locals())` y en Cookiecutter `mocker.patch('modulo.funcion')`: **referencias por nombre que el análisis estático no ve**.

> El código original en `tornado/` **nunca se modifica**. Todo se hace en `rope_pruebas/_trabajo/<experimento>/`.

---

## 2. Cómo ejecutarlo

Desde la raíz del repositorio:

```bash
# (una sola vez) crear el entorno con Python 3.12, Rope y CodeCarbon
~/Library/Python/3.9/bin/uv venv --python 3.12 .venv
~/Library/Python/3.9/bin/uv pip install --python .venv/bin/python rope codecarbon

# La extensión C tornado/speedups.abi3.so es opcional (sin ella Tornado usa la
# versión en Python puro). Aquí ya estaba compilada; ver la nota de abajo.

# 1) Línea base "a mano" (opcional, el script también la hace)
PYTHONPATH=. .venv/bin/python -m tornado.test.runtests

# 2) Todo el proceso: reposo + línea base + análisis estático + refactorizaciones + carbono
.venv/bin/python -u rope_pruebas/ejecutar_pruebas_rope.py
```

Tarda unos **8 minutos**: 21 corridas de la suite (~18 s cada una) y 91 operaciones de Rope. Cada ejecución **borra y regenera** la carpeta `resultados/`. Variables de entorno opcionales: `CODECARBON_PAIS` (por defecto `COL`) y `CODECARBON_TDP` (por defecto `20`).

> En esta máquina la extensión `tornado/speedups.abi3.so` ya estaba compilada (quedó de una instalación editable previa). Está en `.gitignore`, y el script la copia junto con el resto de `tornado/`.

### 2.1 Problema encontrado: la instalación editable contamina el experimento

En una primera corrida, Tornado estaba instalado en el `.venv` con `pip install -e .` (igual que Cookiecutter con `uv sync`). La refactorización 19 (renombrar el módulo `tornado/locks.py` → `tornado/sync.py`) dio **"comportamiento preservado"**, lo que no tenía sentido: `tornado/__init__.py` seguía listando `"locks"`.

La causa: la instalación editable de setuptools registra un *finder* (`__editable___tornado_6_7_dev1_finder.py`). Cuando un submódulo **no existe** en la copia, ese finder lo busca **en el repositorio original**:

```
$ cd _trabajo/19_rename_modulo && PYTHONPATH=$PWD python -c "import tornado.locks as l; print(l.__file__)"
/Users/estebangarrido10/tornado_tesis/tornado/locks.py      ← ¡el original, no la copia!
```

`PYTHONPATH` tapa el paquete `tornado` completo, pero no un submódulo que falta. Solución: **desinstalar Tornado del `.venv`** (`uv pip uninstall tornado`). Rope y CodeCarbon no lo necesitan y la copia se importa solo vía `PYTHONPATH`. El script ahora lo comprueba al iniciar (`verificar_sin_tornado_instalado`) y aborta si encuentra Tornado instalado. **Todos los resultados de este documento son de la corrida limpia.**

Esto también afecta a Cookiecutter en teoría (allí sí estaba instalado en modo editable), pero ninguna de sus refactorizaciones borraba o renombraba un módulo, así que sus resultados no cambian.

### 2.2 Detalles técnicos del script

- **`python -m tornado.test.runtests`**: el runner oficial. El script lee las líneas `Ran N tests` y `OK (skipped=K)` / `FAILED (failures=F, errors=E, skipped=K)`. `passed = N − F − E − K`. Si el runner no llega a imprimir `Ran`, por ejemplo por un `SyntaxError` al importar, se cuenta como 1 error.
- **`PYTHONPATH=<copia>`**: hace que se importe el Tornado de la copia. El script lo verifica (la ruta aparece en la consola). Los tests que lanzan subprocesos (`import_test`, `autoreload_test`, `process_test`) heredan la variable.
- **`Project(..., ignore_syntax_errors=True)`**: la misma opción que en Cookiecutter, por robustez. En Tornado no hubo archivos `.py` inválidos.
- La copia excluye `docs/`, `demos/`, `maint/`, `.github/`, `.git/` y `.venv/`, que los tests no usan.

### 2.3 Cómo se mide el carbono

Se crea **un solo** `OfflineEmissionsTracker` para todo el experimento, porque su inicialización tarda unos 18 s. Cada fase se mide como una *task* (`tracker.start_task()` / `tracker.stop_task()`):

| Fase | Qué incluye | Repeticiones |
|---|---|---|
| `reposo` | `time.sleep(20)` | 1 |
| `tests` (línea base) | una corrida completa de la suite original | 3 |
| `analisis` | todo el análisis estático (sección 4) | 1 |
| `rope` | `funcion(proyecto)` (calcular los cambios) + `proyecto.do(cambios)` (escribirlos). **No** incluye copiar el proyecto ni abrirlo. | 5 por refactorización |
| `tests` (refactorización) | una corrida de la suite sobre la copia refactorizada | 1 |

#### Medición durante la ejecución (traza de 0,1 s)

**Problema:** dentro de una *task*, CodeCarbon calcula la energía **una sola vez, al llamar a `stop_task`**, con la carga media de un monitor que muestrea cada 1 s. Se obtiene el total "después de la ejecución", pero no se ve qué pasó durante ella, y una operación de menos de 1 s casi no deja muestras.

**Solución:** el módulo [`carbono_traza.py`](carbono_traza.py) (clase `Medidor`, compartida con `../llm_pruebas/`) envuelve el tracker y, mientras corre cada fase, lanza un hilo que **cada 0,1 s** lee la carga de CPU de todo el equipo y calcula la potencia instantánea con el mismo modelo que CodeCarbon usa en este Mac (`P_cpu = TDP × (0,1 + 0,9 × carga³)` y `P_ram = 3 W`). La energía de la fase es la integral de esas muestras. Cada muestra se guarda en `resultados/traza_carbono.csv` (fase, tiempo, carga, potencia, energía y emisiones acumuladas), y en `carbono.csv` y `resumen.md` quedan columnas nuevas: muestras, energía de la traza y **pico de potencia**.

**Validación cruzada:** la traza integrada da **0,619 Wh** para todo el experimento y CodeCarbon **0,631 Wh** (diferencia ≈ 2 %).

**Límite:** 15 de las 91 operaciones de Rope duran menos de 0,1 s (las extracciones 07, 08 y 10 y el rechazo 09), así que **no dejan ninguna muestra**: su curva no existe y su energía es prácticamente cero. Las demás tienen entre 1 y 8 muestras por operación.

Configuración de CodeCarbon y por qué:

| Parámetro | Valor | Motivo |
|---|---|---|
| `OfflineEmissionsTracker` | — | No envía datos a internet. El factor de emisión sale de la tabla interna de CodeCarbon. |
| `country_iso_code` | `COL` | Red eléctrica de Colombia: **259,5 g CO2eq/kWh** (dato de 2023 en `global_energy_mix.json`: 63 % hidroeléctrica, 20 % gas, 10 % carbón). |
| `tracking_mode` | `machine` | Mide la carga de **todo el equipo**. Es obligatorio porque los tests corren en un subproceso: en modo `process` solo se contaría el proceso del script. |
| `measure_power_secs` | `1` | Muestrea la carga cada segundo (el valor por defecto es 15 s, demasiado para operaciones de menos de 1 s). |
| `force_cpu_power` | `20` | Ver el problema de abajo. |
| `force_mode_cpu_load` | `True` | Usar el modelo basado en carga de CPU. |

**Cómo estima CodeCarbon la energía en este Mac.** Sin `sudo` no puede leer `powermetrics` (el medidor real de Apple), así que **no mide: estima**:

- CPU: `P_cpu = TDP × (0,1 + 0,9 × carga³)`, donde `carga` es el % de uso de CPU de toda la máquina (`psutil`).
- RAM: potencia constante de **3 W** (modelo de estimación por GB de RAM para ARM).
- Energía = potencia × tiempo. Emisiones = energía × 259,5 g/kWh.

**Problema encontrado: CodeCarbon no reconoce el Apple M4.** Su tabla `data/hardware/cpu_power.csv` tiene `Apple M4,20`, pero la búsqueda difusa también encuentra `Apple M4 Pro`, `M4 Max` y `M4 Ultra` con la misma similitud. Al ver el empate, descarta el resultado y usa un valor genérico de **10 hilos × 8,5 W = 85 W**, es decir, 4,25 veces el TDP real. Por eso se fuerza `force_cpu_power=20`, el valor de la propia tabla de CodeCarbon. El script también calcula cuánto habría reportado CodeCarbon sin la corrección (sección 6.4).

### Estructura de archivos

```
rope_pruebas/
├── README.md                    ← este documento
├── RESUMEN_PRESENTACION.md      ← versión corta para presentar
├── ejecutar_pruebas_rope.py     ← script que automatiza todo
├── .gitignore                   ← ignora _trabajo/
├── _trabajo/                    ← copias del proyecto, una por experimento (temporal)
└── resultados/
    ├── resumen.md               ← tabla resumen + carbono (se genera sola)
    ├── resumen.json             ← los mismos datos en JSON (para gráficos o tablas de la tesis)
    ├── carbono.csv              ← una fila por medición de CodeCarbon (114 filas)
    ├── traza_carbono.csv        ← potencia cada 0,1 s durante cada fase (~4 000 filas)
    ├── 00_linea_base_tests.txt  ← salida completa de la suite en la línea base
    ├── 01_analisis_estatico.md  ← resultados de find_errors / find_occurrences / find_definition
    ├── NN_<nombre>.diff         ← cambios exactos que hizo Rope
    ├── NN_<nombre>_tests.txt    ← salida de la suite después de la refactorización
    └── NN_<nombre>_error.txt    ← traceback, si Rope rechazó la refactorización
```

---

## 3. Paso 1: línea base (tests de Tornado sin cambios)

| Resultado | Cantidad |
|---|---|
| Ejecutados | 1535 |
| Passed | **1424** |
| Failed | 0 |
| Skipped | 111 |
| Errors | 0 |

Las 3 corridas dieron exactamente el mismo resultado (18,4 s de media). Los 111 tests omitidos dependen de módulos opcionales no instalados (`pycurl`, `twisted`, `pycares`, `hypothesis`) o de la plataforma (sockets *abstract namespace* de Linux, decodificación `br`).

**Limitación del oráculo:** uno de los omitidos es `api_test`, que compara la API pública con la instantánea `tornado/test/api.txt`, pero solo corre en Linux con CPython. En Linux, los Rename 02, 03 y 05 de nombres públicos **también romperían ese test**. En macOS ese test no se ejecuta, así que la suite no detecta el cambio de API pública.

**Referencia para comparar: 1424 passed / 0 failed / 111 skipped.**

---

## 4. Paso 2: análisis estático con Rope

Detalle completo en [`resultados/01_analisis_estatico.md`](resultados/01_analisis_estatico.md). Todo el análisis tardó 1,9 s.

### 4.1 `find_occurrences`: búsqueda de referencias

| Símbolo | Ocurrencias encontradas | ¿Correcto? |
|---|---|---|
| `httputil.url_concat` | 20 | **Incompleto:** no cuenta las 3 llamadas de su propio doctest (ver 5.3, caso 02) |
| `netutil.is_valid_ip` | 20 | Sí |
| `util.Configurable` | 26 | **Incompleto:** no ve el string `"_Configurable__impl_class"` ni la anotación en string `"Union[None, str, Type[Configurable]]"` (ver 5.3, caso 05) |
| `BaseIOStream._try_inline_read` | 6 | **Incompleto:** no ve el `mock.patch("tornado.iostream.BaseIOStream._try_inline_read")` (caso 13) |
| `httputil._normalize_header` | 7 | **Incompleto:** no ve la llamada del doctest (caso 14) |
| `httputil.doctests` | 1 (solo la definición) | **Incompleto:** no ve `"tornado.httputil.doctests"` en `runtests.TEST_MODULES` (caso 16) |

Ninguna ocurrencia salió marcada como "dudosa" (`unsure`). Rope no da ningún aviso de que podría haber más referencias.

### 4.2 `find_definition`: ir a la definición

Desde la llamada `return url_concat(url, args)` en `tornado/auth.py`, Rope resuelve bien la definición en `tornado/httputil.py:801`.

### 4.3 `find_errors`: detección de errores

Rope reporta **423 avisos** en los 35 módulos (`web`: 62, `options`: 42, `httputil`: 40, `iostream`: 35, `auth`: 34, `testing`: 25…). El código funciona y la suite pasa completa. Por su cantidad no se revisaron uno por uno como en PySnooper (31) y Cookiecutter (39). Se agruparon por tipo de aviso y se revisaron los nombres más repetidos:

| Tipo de aviso | Cant. | Nombres más frecuentes | Por qué es falso positivo |
|---|---|---|---|
| `Unresolved attribute` | 277 | `_options` (22), `pattern` (21), `AddressFamily` (19), `__class__` (10), `fullmatch` (9) | Rope no infiere tipos de la biblioteca estándar (`re.Pattern`, `socket.AddressFamily`) ni atributos creados con `self.__dict__[...]` (`options.py`) |
| `Unresolved variable` | 79 | `f`, `opt`, `n` | Variables de comprensiones y generadores, y nombres definidos de forma dinámica |
| `Defined later` | 67 | `k` (13), `i` (10), `v` (7) | El mismo error de alcance de comprensiones que en PySnooper y Cookiecutter |

Igual que en los dos proyectos anteriores, no se encontró ningún error real entre los avisos revisados. La tasa de avisos es de 16 por cada 1000 líneas (PySnooper: 32; Cookiecutter: 14).

---

## 5. Paso 3: refactorizaciones automáticas

### 5.1 Resultados

| # | Tipo | Qué se hizo | Archivos modificados | Tests (passed/failed+errors) | Veredicto |
|---|---|---|---|---|---|
| 02 | Rename | `httputil.url_concat` → `concat_url_args` | 5 | 1423 / **1** | ❌ Rompe tests (doctest) |
| 03 | Rename | `netutil.is_valid_ip` → `is_ip_address` (importada por tests y `caresresolver`) | 5 | 1424 / 0 | ✅ Preservado |
| 04 | Rename | método `BaseIOStream._maybe_add_error_listener` → `_ensure_error_listener` | 1 | 1424 / 0 | ✅ Preservado |
| 05 | Rename | clase `util.Configurable` → `ConfigurableBase` (base de `IOLoop`, `AsyncHTTPClient`, `Resolver`) | 6 | 1419 / **5** | ❌ Rompe tests |
| 06 | Rename | parámetro `plus` de `escape.url_escape` → `use_plus` (pasado por nombre) | 4 | 1424 / 0 | ✅ Preservado |
| 07 | Extract Method | quitar comillas del boundary → `_unquote_boundary` | 1 | 1424 / 0 | ✅ Preservado |
| 08 | Extract Method | separar unidad y valor del header Range → `_split_range_header` (2 valores de salida) | 1 | 1424 / 0 | ✅ Preservado |
| 09 | Extract Method | `try/except` con `return None` en medio de `_parse_request_range` (caso límite) | — | — | ⛔ Rechazada por Rope |
| 10 | Extract Method | bucle que copia argumentos urlencoded → `_merge_urlencoded_arguments` | 1 | 1424 / 0 | ✅ Preservado |
| 11 | Inline | `httputil._int_or_none` en `_parse_request_range` (2 llamadas) | 1 | 1401 / **23** | ❌ Rompe tests |
| 12 | Move | `tcpclient._format_addr` → módulo `netutil` | 3 | 1424 / 0 | ✅ Preservado (con error latente, ver 5.2) |
| 13 | Rename | `BaseIOStream._try_inline_read` → `_read_inline_if_possible` (parcheado por string) | 1 | 1421 / **3** | ❌ Rompe tests |
| 14 | Rename | `httputil._normalize_header` → `_to_header_case` (tiene doctest) | 1 | 1423 / **1** | ❌ Rompe tests |
| 15 | Rename | igual que 14, con `docs=True` | 1 | 1424 / 0 | ✅ Preservado |
| 16 | Rename | `httputil.doctests` → `doctest_suite` (nombrada en `TEST_MODULES`) | 1 | 1411 / **1** (12 tests dejan de correr) | ❌ Rompe tests |
| 17 | Rename | método `get` de `HelloHandler` → `handle_get` (despacho por `getattr`) | 1 | 1423 / **1** | ❌ Rompe tests |
| 18 | Rename | clase `HelloHandler` → `GreetingHandler` (nombrada como string en una ruta) | 1 | 1423 / **1** | ❌ Rompe tests |
| 19 | Rename | módulo `tornado/locks.py` → `tornado/sync.py` | 10 | 1423 / **1** | ❌ Rompe tests |
| 20 | Extract Method | bloque con `await` de `RequestHandler._execute` (`async def`) → `_run_prepare` | 1 | 0 / **1** (la suite no arranca) | ❌ Rompe tests |

**Totales:**

- **Casos equivalentes a PySnooper y Cookiecutter (02–12): 7 de 11 preservan el comportamiento (64 %).** 3 rompen tests y 1 la rechaza Rope.
- **Casos propios de Tornado (13–20): 1 de 8 preservan** (solo 15, gracias a `docs=True`).
- **Total: 8 de 19 (42 %).**
- Cada operación de Rope tardó en promedio 0,8 s (de 0,01 s en 09 a 2,0 s en 17). Los Rename y Move recorren todo el proyecto, así que son mucho más lentos que los Extract Method, que solo analizan un archivo (0,03–0,6 s).

### 5.2 Las refactorizaciones que funcionaron

- **03:** Rope actualizó la definición, los usos en `simple_httpclient` y `httpserver`, el `from tornado.netutil import Resolver, is_valid_ip` de `platform/caresresolver.py` y los tests.
- **04:** el método privado solo se usa dentro de `iostream.py`. Rope cambió la definición y sus 3 usos y no tocó el comentario de `iostream_test.py:386` que lo menciona. Fue correcto no tocarlo, porque es solo texto.
- **06:** Rope renombró el parámetro **y los argumentos por nombre** en los llamadores (`url_escape(x, plus=False)` → `url_escape(x, use_plus=False)` en `routing.py`, `escape_test.py` y `property_test.py`). Distinguió bien el parámetro homónimo de `url_unescape`, que no cambió: `url_unescape(url_escape(b, use_plus=plus), None, plus=plus)`.
- **07, 08 y 10:** extracciones correctas. Rope calculó bien los parámetros y los valores de retorno. En 08 devolvió `unit, value` y descartó correctamente `_`, que no se usa después. Igual que en los proyectos anteriores, deja **una sola línea en blanco** antes de la función nueva (PEP 8 pide dos) y no agrega anotaciones de tipo, aunque todo el resto de Tornado está anotado.
- **12, Move: los tests pasan, pero Rope introdujo un error latente** ([diff](resultados/12_move_funcion.diff)):
  - Movió la función, cambió los usos por `netutil._format_addr(...)`, agregó `from tornado import gen, netutil` y actualizó el import del test. Todo correcto.
  - Además, **borró `Tuple` de `from typing import Any, Tuple`** en `tcpclient.py`, porque creyó que ya no se usaba. Sí se usa, pero dentro de anotaciones escritas como string: `-> "Future[Tuple[socket.AddressFamily, Any, IOStream]]"`.
  - En ejecución no falla, porque Python no evalúa esas anotaciones. Pero `typing.get_type_hints(_Connector.start)` ahora lanza `NameError: name 'Tuple' is not defined`, y `mypy`, que el proyecto usa en CI, lo reportaría. En el código original esa llamada funciona.
  - Es un cambio **que nadie pidió**, en una línea que no tiene relación con la función movida.

### 5.3 Por qué fallan 02, 05, 11, 09 y 20

**02 y 14, Rename de una función con doctest: Rope no renombra dentro del docstring** ([diff 02](resultados/02_rename_funcion.diff), [diff 14](resultados/14_rename_con_doctest.diff)).

```python
def concat_url_args(url: str, args: ...) -> str:     # ← renombrada
    """Concatenate url and arguments regardless of whether
    url has existing query parameters.

    >>> url_concat("http://example.com/foo", dict(c="d"))  # ← el doctest sigue con el nombre viejo
```

La suite de Tornado ejecuta los doctests de `httputil` (vía `TEST_MODULES`), y fallan con `NameError: name 'url_concat' is not defined`. En 02, Rope cambió bien 5 archivos y 20 referencias de código, y solo falló en el docstring. **La opción `docs=True` sí lo resuelve** (caso 15): el nombre es visible en el ámbito del módulo, así que Rope renombra también dentro del docstring. Esto **contrasta con Cookiecutter**, donde `docs=True` no sirvió porque los strings estaban en archivos que no importaban el nombre.

**05, Rename de clase con *name mangling* manual: error silencioso en producción** ([diff](resultados/05_rename_clase.diff)).

`Configurable` guarda la clase configurada en un atributo privado `__impl_class`. Python lo transforma en `_Configurable__impl_class` (*name mangling*: el nombre de la clase forma parte del nombre del atributo). Pero `configured_class` lo busca **escribiendo el nombre transformado como string**:

```python
# tornado/util.py:413
if base.__dict__.get("_Configurable__impl_class") is None:
    base.__impl_class = cls.configurable_default()
```

Rope renombró la clase y los 26 usos de código. Al cambiar el nombre de la clase, Python ahora guarda el atributo como `_ConfigurableBase__impl_class`, pero el string sigue buscando `_Configurable__impl_class`. Resultado: **`configured_class()` cree que nunca se configuró nada y siempre devuelve la clase por defecto**. `IOLoop.configure(...)`, `AsyncHTTPClient.configure(...)` y `Resolver.configure(...)` dejan de funcionar sin ningún error. 5 tests de `ConfigurableTest` lo detectan (`TestConfig1 is not an instance of TestConfig2`).

Además, Rope dejó sin cambiar la anotación en string `impl: "Union[None, str, Type[Configurable]]"` de `httpclient.py:316`. `typing.get_type_hints(AsyncHTTPClient.configure)` ahora lanza `NameError: name 'Configurable' is not defined`. Es el mismo tipo de error latente que en 12.

**11, Inline: Rope borra la función y deja las llamadas** ([diff](resultados/11_inline_funcion.diff)). Es el error más grave del experimento.

```diff
-def _int_or_none(val: str) -> int | None:
-    val = val.strip()
-    if val == "":
-        return None
-    return int(val)
```

Es el **único** cambio del diff. Las dos llamadas `start = _int_or_none(start_b)` y `end = _int_or_none(end_b)` (`httputil.py:899-900`) quedan intactas, apuntando a una función que ya no existe. Rope no dio ningún aviso ni lanzó ninguna excepción: `get_changes()` devolvió un ChangeSet "válido".

Causa probable: la función tiene **dos `return`** (uno temprano y uno final) y **reasigna su parámetro**, que es el mismo patrón que hizo fallar el Inline en Cookiecutter. En Cookiecutter Rope generó código incorrecto. Aquí, aparentemente, no supo generar el cuerpo para los llamadores y solo aplicó la parte de "borrar la definición".

Efecto: cualquier petición HTTP con header `Range` produce `NameError` → **error 500**. 23 tests fallan: el doctest de `_parse_request_range` y 22 tests de `StaticFileTest` (`AssertionError: 500 != 206`).

**09, Extract Method con `return` en medio: Rope se niega, y está bien.** El bloque `try: ... except ValueError: return None` tiene un `return` que debe salir de `_parse_request_range`. Si se extrajera tal cual, el `return None` saldría solo de la función nueva y `_parse_request_range` seguiría ejecutándose. Rope responde `RefactoringError: Return should be the last statement.` y no modifica nada. Es un **fallo seguro**, igual que el `continue` de Cookiecutter (09).

**20, Extract Method de código con `await`: Rope genera código que ni siquiera compila** ([diff](resultados/20_extract_await.diff)).

```python
            self._run_prepare()  # type: ignore     # ← llamada sin await

    def _run_prepare(self):                         # ← def, no async def
        result = self.prepare()
        if result is not None:
            result = await result  # type: ignore   # ← SyntaxError
```

Rope cometió tres errores en un solo cambio:

1. Creó un `def` normal en lugar de `async def`, aunque el bloque contiene `await`.
2. Llamó a la función sin `await`.
3. Movió el comentario `# type: ignore` a la línea de la llamada.

Al importar `tornado.web` aparece `SyntaxError: 'await' outside async function`. **La suite entera no puede arrancar** (0 tests ejecutados). Es el fallo más visible, pero también el más fácil de detectar: cualquier import lo revela. Esto es relevante para Tornado, cuyo núcleo (`RequestHandler._execute`, `IOStream`, `TCPClient`, `HTTPServer`) es casi todo `async def`.

### 5.4 Referencias por nombre (strings) que Rope no ve: 13, 16, 17, 18 y 19

En los cinco casos Rope aplicó el cambio sin avisar y **todas las referencias de código quedaron bien**. Solo falló el acceso por nombre:

| # | Qué cambió Rope | Referencia que no vio | Error al correr los tests |
|---|---|---|---|
| 13 | `_try_inline_read` en `iostream.py` (6 ocurrencias) | `mock.patch("tornado.iostream.BaseIOStream._try_inline_read")` en `iostream_test.py:931` | `AttributeError: <class 'BaseIOStream'> does not have the attribute '_try_inline_read'` (3 tests: TCP, SSL y SSLContext) |
| 16 | `def doctests()` → `def doctest_suite()` | `"tornado.httputil.doctests"` en `runtests.TEST_MODULES` | `AttributeError: module 'tornado.httputil' has no attribute 'doctests'`. Además, **los 12 doctests de `httputil` dejan de ejecutarse** (1535 → 1523 tests), así que el oráculo pierde cobertura en silencio. |
| 17 | `def get(self)` → `def handle_get(self)` en `HelloHandler` | `getattr(self, self.request.method.lower())` en `web.py`: el nombre del método **es** el verbo HTTP | La ruta responde **405 Method Not Allowed** en vez de `hello` |
| 18 | `class HelloHandler` → `class GreetingHandler` y la ruta `("/hello1", HelloHandler)` | `("/hello2", "tornado.test.web_test.HelloHandler")` y `url("/hello3", "...HelloHandler")`, que se resuelven con `import_object` | `ImportError: No module named HelloHandler` |
| 19 | Movió `locks.py` → `sync.py` y actualizó **10 archivos** de imports (`queues.py` y 9 de tests) | `"locks"` en `tornado.__all__` (`__init__.py:45`) y `locks` en el stub `__init__.pyi` | `test_import_everything`: `ModuleNotFoundError: No module named 'tornado.locks'`. Además, `tornado.locks` deja de existir como API pública. |

El caso 17 es especialmente ilustrativo: **renombrar un método es correcto para Rope, pero en Tornado el nombre del método es un contrato con el framework**. Rope no tiene forma de saberlo.

---

## 6. Huella de carbono (CodeCarbon)

Datos completos en [`resultados/carbono.csv`](resultados/carbono.csv) (una fila por medición) y [`resultados/resumen.md`](resultados/resumen.md).

### 6.1 Totales del experimento

| Concepto | Duración (s) | Energía (Wh) | Emisiones (mg CO2eq) | % de la energía |
|---|---|---|---|---|
| 91 operaciones de Rope | 63,4 | 0,097 | 25,3 | 15 % |
| Análisis estático | 2,3 | 0,004 | 0,9 | 1 % |
| 21 corridas de la suite de tests | 377,3 | 0,530 | 137,4 | 84 % |
| **Experimento completo** | **443,0** | **0,631** | **163,6** | 100 % |

**Todo el experimento emitió ≈ 0,16 g de CO2eq** con la red eléctrica de Colombia (0,63 Wh).

> Estas cifras son de la **corrida del 2026-11-13**, que repitió el experimento completo con la medición continua (los veredictos de las 19 refactorizaciones salieron idénticos a los de la corrida anterior). Las cifras de energía cambian ligeramente entre corridas (la anterior dio 0,73 Wh) por el ruido de fondo del equipo. Durante esta corrida había otro proyecto con actividad en el mismo Mac (`black_tesis`) y no se verificó en qué momentos exactos; como la medición es de todo el equipo (`machine`), no se puede descartar algo de ruido. Los picos de Rope (máx. 9,6 W) son bajos, así que no se observa una perturbación grande.

### 6.2 Costo por operación

| Medición | Duración | Energía | Emisiones | Desv. estándar |
|---|---|---|---|---|
| Una operación de Rope (media de 91) | 0,70 s | 0,0011 Wh | **0,28 mg CO2eq** | 0,23 mg |
| Una corrida de la suite (media de 3 en línea base) | 18,4 s | 0,0265 Wh | **6,87 mg CO2eq** | 0,25 mg |
| Reposo (20 s) | 20,0 s | 0,0279 Wh | 7,24 mg CO2eq | — |

Por tipo de operación de Rope (media de 5 repeticiones, ver `resumen.md`):

| Operación | Tiempo | Emisiones |
|---|---|---|
| Rename de función/clase/método (02–06, 13–16, 18) | 0,5 – 1,2 s | 0,19 – 0,65 mg |
| Rename del método `get` (17) | 1,6 s | 0,58 mg (el más lento; probablemente porque `get` es un nombre muy común y Rope tiene que descartar muchas más candidatas en todo el proyecto) |
| Rename de módulo (19) | 1,4 s | 0,52 mg |
| Move (12) | 0,9 s | 0,34 mg |
| Extract Method (07, 08, 10, 20) | 0,03 – 0,6 s | 0,01 – 0,21 mg |
| Rechazo (09) | 0,006 s | 0,002 mg |

### 6.3 Interpretación

1. **Verificar cuesta mucho más que refactorizar.** Una corrida de la suite emite unas **25 veces más** que una operación de Rope (6,9 mg frente a 0,28 mg). El 84 % de la energía del experimento se fue en correr tests. Aplicar Rope sin verificar sería casi gratis, pero según la sección 5 eso no es seguro (11 de 19 casos rompen algo).
2. **La huella absoluta es muy pequeña.** 0,28 mg de CO2eq por refactorización, y 0,16 g para las 19 refactorizaciones con sus 5 repeticiones y todas las verificaciones.
3. **La energía es, en la práctica, duración × potencia base.** En este equipo, la suite de tests consume en promedio **5,05 W**, prácticamente lo mismo que el equipo **en reposo (5,02 W)**. La suite corre en un solo hilo y espera mucho en E/S (sockets locales), y con el modelo cúbico (`carga³`) un núcleo ocupado de 10 casi no sube la estimación. Rope promedia **5,53 W**, con un pico de 9,6 W que la traza de 0,1 s sí captura (con el muestreo de 1 s habría pasado desapercibido). Por eso el consumo es proporcional al tiempo y **reducir el tiempo de la suite es lo que más reduce la huella**.
4. **El resultado depende del modelo.** La energía neta por encima del reposo es de ≈ 32 J para todas las operaciones de Rope y está dentro del ruido para los tests. Con estimaciones basadas en TDP no se puede separar el consumo de la tarea del consumo de fondo del Mac (VS Code, navegador, etc.), porque el modo `machine` mide todo el equipo.

### 6.4 Limitaciones de la medición

- **Es una estimación, no una medición.** Sin `sudo` no hay acceso a `powermetrics` ni a los contadores RAPL. CodeCarbon infiere la potencia a partir del % de CPU y un TDP de tabla.
- **Sensibilidad al TDP:** con el TDP genérico de 85 W que CodeCarbon usa por defecto en este equipo (sección 2.3), el experimento completo habría reportado **1,48 Wh y 384 mg CO2eq**, 2,3 veces más. Sin la corrección, las cifras estarían infladas.
- **La RAM se modela con potencia constante (3 W)**, independientemente del uso real. Es más de la mitad de la potencia estimada en reposo.
- **Modo `machine`:** incluye cualquier otro proceso del equipo. La medición del reposo (5,02 W) da la referencia de ese ruido de fondo.
- **Factor de emisión:** 259,5 g/kWh es el promedio anual de la red colombiana en 2023. Con otro país el resultado cambia proporcionalmente: `CODECARBON_PAIS=USA`, `FRA`, etc.
- **No incluye** la energía de la pantalla, de la fabricación del equipo ni de la red.

---

## 7. Conclusiones

1. **Rope es confiable cuando todas las referencias son código Python.** Las refactorizaciones que solo tocaban código (03, 04, 06, 07, 08, 10, 12) preservaron el comportamiento, incluso con cambios que cruzan 4 y 5 archivos (03, 06) y con argumentos por nombre (06).
2. **En Tornado hay muchas referencias por nombre**, y Rope no ve ninguna: doctests (02, 14), *name mangling* escrito a mano (05), `mock.patch` (13), listas de módulos de tests (16), despacho de verbos HTTP por `getattr` (17), handlers como strings (18) y `__all__` con import perezoso (19). Es el mismo patrón que en PySnooper (`locals()`) y Cookiecutter (mocks por string), pero mucho más frecuente, porque Tornado es un **framework**: su diseño se basa en convenciones de nombres.
3. **`docs=True` sirve para doctests** (15), porque el nombre es visible en el módulo. No sirve para strings en otros archivos (Cookiecutter 14, y por diseño tampoco ayudaría en 13, 16 y 18).
4. **Inline es la operación menos confiable:** en Tornado borró la función y dejó llamadas colgando (11). En Cookiecutter cambió el comportamiento en silencio. En PySnooper fue la única que funcionó.
5. **Extract Method no entiende `async`/`await`** (20). En Tornado esto es una limitación de fondo, porque casi todo el núcleo es asíncrono.
6. **Rope hace cambios no pedidos que rompen anotaciones en string** (12: borra `Tuple`; 05: deja `Type[Configurable]`). La suite no lo detecta, pero `mypy` y `typing.get_type_hints` sí. Conviene correr `mypy` además de los tests después de Rope.
7. **Los fallos seguros existen** (09: `return` en medio). Rope avisa y no cambia nada, igual que con `continue` en Cookiecutter.
8. **`find_errors` no sirve para encontrar errores:** 423 avisos, ninguno real entre los revisados.
9. **Huella de carbono:** cada refactorización de Rope emite ≈ 0,4 mg CO2eq (red colombiana) y verificarla con la suite ≈ 7,4 mg, unas 18 veces más. El costo ambiental de Rope es despreciable. El de la verificación domina, y sigue siendo indispensable.
10. **Lecciones metodológicas:** (a) una instalación editable puede hacer pasar en falso una refactorización que borra módulos (sección 2.1); (b) CodeCarbon necesita una revisión manual del TDP en Apple Silicon (sección 2.3).

### Comparación con PySnooper y Cookiecutter

| | PySnooper | Cookiecutter | Tornado |
|---|---|---|---|
| Tamaño | 964 líneas, 5 módulos, 83 tests | 2806 líneas, 18 módulos, 379 tests | 25 996 líneas, 35 módulos, 1424 tests |
| Casos equivalentes (02–12) que preservan | 8/11 (73 %) | 8/11 (73 %) | **7/11 (64 %)** |
| Rename (02–06) | 5/5 | 5/5 | **3/5** (doctest, name mangling) |
| Extract Method (07–10) | 1/4 | 2/4 (+1 rechazada) | 3/4 (+1 rechazada) |
| Inline (11) | 1/1 | 0/1 (cambia comportamiento) | **0/1 (borra la función y deja las llamadas)** |
| Move (12) | 1/1 | 1/1 | 1/1 (con error latente en anotaciones) |
| Casos propios del proyecto | — | 0/3 (mocks por string) | 1/8 (strings, doctests, `getattr`, `async`) |
| Causa principal de los fallos | `.format(**locals())` | mocks por string; flujo de datos | referencias por nombre propias de un framework; `async` |
| Avisos de `find_errors` (falsos positivos) | 31/31 | 39/39 | 423 (ninguno real entre los revisados) |
| Obstáculo extra | — | archivos `.py` que son plantillas Jinja | instalación editable que contamina; TDP de CodeCarbon |
| Huella de carbono | — | — | 0,4 mg CO2eq/op. Rope; 7,4 mg/corrida de tests |

---

## 8. Cómo agregar una refactorización nueva

En `ejecutar_pruebas_rope.py`:

1. Escribe una función que reciba el proyecto Rope `p` y devuelva los cambios:

   ```python
   def ref_mi_prueba(p):
       r = p.get_resource('tornado/escape.py')
       offset = offset_de(r, 'def squeeze', 4)   # apunta al nombre
       return Rename(p, r, offset).get_changes('collapse_whitespace')
   ```

   - `offset_de(recurso, marcador, desplazamiento)` busca un texto **único** en el archivo y devuelve su posición. El desplazamiento mueve el cursor hasta el nombre (`'def '` = 4, `'class '` = 6).
   - Para Extract Method se necesita un rango `(inicio, fin)`. Ver `ref_extract_boundary` como ejemplo (`inicio_de_linea` y `linea_anterior` ayudan a calcularlo).
   - Para renombrar un **módulo**, se omite el offset: `Rename(p, recurso_del_archivo).get_changes('nuevo_nombre')`.

2. Agrégala a la lista `REFACTORIZACIONES`:

   ```python
   ('21_mi_prueba', 'Rename', 'escape.squeeze -> collapse_whitespace', ref_mi_prueba),
   ```

3. Vuelve a correr el script. La fila nueva y su consumo aparecen en `resultados/resumen.md` y `resultados/carbono.csv`.

### API usada (referencia rápida)

| Operación | Clase / función | Llamada |
|---|---|---|
| Abrir proyecto | `rope.base.project.Project` | `Project(ruta, ignore_syntax_errors=True)` … `proyecto.close()` |
| Renombrar | `rope.refactor.rename.Rename` | `Rename(p, recurso, offset).get_changes('nuevo', docs=False)` |
| Renombrar módulo | `rope.refactor.rename.Rename` | `Rename(p, recurso).get_changes('nuevo')` |
| Extraer método | `rope.refactor.extract.ExtractMethod` | `ExtractMethod(p, recurso, inicio, fin).get_changes('nombre')` |
| Inline | `rope.refactor.inline.create_inline` | `create_inline(p, recurso, offset).get_changes()` |
| Mover | `rope.refactor.move.create_move` | `create_move(p, recurso, offset).get_changes(recurso_destino)` |
| Aplicar cambios | — | `p.do(cambios)` |
| Ver diff | — | `cambios.get_description()` |
| Buscar usos | `rope.contrib.findit.find_occurrences` | `find_occurrences(p, recurso, offset)` |
| Ir a definición | `rope.contrib.findit.find_definition` | `find_definition(p, codigo, offset, recurso)` |
| Buscar errores | `rope.contrib.finderrors.find_errors` | `find_errors(p, recurso)` |
| Tracker de carbono | `codecarbon.OfflineEmissionsTracker` | `OfflineEmissionsTracker(country_iso_code='COL', tracking_mode='machine', force_cpu_power=20, ...)` |
| Medir una fase | — | `tracker.start_task('nombre')` … `datos = tracker.stop_task()` → `datos.energy_consumed` (kWh), `datos.emissions` (kg) |
