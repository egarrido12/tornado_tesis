# Rope sobre Tornado: resumen para presentar

Detalle completo en [README.md](README.md). Datos en [`resultados/`](resultados/).

## 1. Qué se hizo

- **Pregunta 1:** ¿las refactorizaciones automáticas de Rope preservan el comportamiento?
- **Pregunta 2:** ¿cuál es su huella de carbono? (medida con CodeCarbon)
- **Sujeto:** Tornado 6.7 (framework web asíncrono): 26 000 líneas, 35 módulos, **1424 tests** que pasan.
- **Método:** 19 refactorizaciones, cada una aplicada con la API de Rope sobre una copia limpia. Después se corre la suite completa.
  - Si pasan los 1424 tests → ✅ preservado.
  - Si falla alguno → ❌ rompe tests.
  - Si Rope se niega → ⛔ rechazada.
- Las refactorizaciones 02–12 son **las mismas categorías** que en PySnooper y Cookiecutter. Las 13–20 son **casos propios de Tornado**.

## 2. Resultado general

| | Preservan |
|---|---|
| Casos equivalentes (02–12) | **7/11 (64 %)** (PySnooper y Cookiecutter: 73 %) |
| Casos propios de Tornado (13–20) | **1/8** |
| **Total** | **8/19 (42 %)** |

## 3. Las 19 pruebas: qué hizo Rope y qué pasó

| # | Refactorización | Qué cambió Rope | Resultado | Por qué |
|---|---|---|---|---|
| 02 | Rename `url_concat` | 5 archivos, 20 referencias | ❌ 1 test | No renombró el nombre dentro de su **doctest** |
| 03 | Rename `is_valid_ip` | 5 archivos (incluye tests y `caresresolver`) | ✅ | — |
| 04 | Rename método privado de `IOStream` | 1 archivo | ✅ | — |
| 05 | Rename clase `Configurable` | 6 archivos, 26 referencias | ❌ 5 tests | El código busca `"_Configurable__impl_class"` **como string** (*name mangling* manual). `IOLoop.configure()` deja de funcionar **en silencio**. |
| 06 | Rename parámetro `plus` | 4 archivos, incluidos argumentos `plus=False` | ✅ | Distinguió bien el parámetro homónimo de `url_unescape` |
| 07 | Extract (1 salida) | nueva función `_unquote_boundary` | ✅ | — |
| 08 | Extract (2 salidas) | `unit, value = _split_range_header(...)` | ✅ | — |
| 09 | Extract con `return` en medio | nada | ⛔ | "Return should be the last statement": **fallo seguro** |
| 10 | Extract de un bucle | nueva función `_merge_urlencoded_arguments` | ✅ | — |
| 11 | Inline `_int_or_none` | **borró la función y dejó las 2 llamadas** | ❌ 23 tests | `NameError` → todo header `Range` da **HTTP 500**. Sin ningún aviso. |
| 12 | Move `_format_addr` | 3 archivos, imports actualizados | ✅ (pero…) | Borró `Tuple` de un import porque solo se usaba en anotaciones string. `mypy` lo reportaría. |
| 13 | Rename método parcheado | 6 ocurrencias | ❌ 3 tests | `mock.patch("...BaseIOStream._try_inline_read")` es un string |
| 14 | Rename con doctest | 7 ocurrencias | ❌ 1 test | Igual que 02 |
| 15 | Igual que 14 con `docs=True` | también el docstring | ✅ | **`docs=True` sí resuelve los doctests** |
| 16 | Rename `httputil.doctests` | 1 línea | ❌ 1 error | `TEST_MODULES` lo nombra como string. Además, **12 tests dejan de correr en silencio**. |
| 17 | Rename método `get` de un handler | 1 línea | ❌ 1 test | Tornado despacha con `getattr(self, "get")` → **405 Method Not Allowed** |
| 18 | Rename clase handler | clase + 1 ruta | ❌ 1 test | Otra ruta la nombra como string `"tornado.test.web_test.HelloHandler"` |
| 19 | Rename módulo `locks` → `sync` | 10 archivos de imports | ❌ 1 test | `tornado.__all__` lista `"locks"` como string |
| 20 | Extract con `await` | `def` (no `async def`), llamada sin `await` | ❌ suite no arranca | `SyntaxError: 'await' outside async function` |

## 4. Patrones de fallo

1. **Referencias por nombre que el análisis estático no ve** (9 de los 11 fallos): doctests, strings en `mock.patch`, `getattr`, handlers como strings, `__all__`, *name mangling* manual. En un framework estas convenciones son el diseño, no excepciones.
2. **Errores silenciosos:** en 05, 11, 16 y 20 Rope no dio ningún aviso. Solo los tests lo revelan.
3. **Errores latentes que ni los tests ven:** 05 y 12 dejan anotaciones de tipo rotas.
4. **`async`/`await` no está soportado por Extract Method** (20). Es crítico en Tornado.
5. **Rope sí sabe rechazar** casos de flujo de control imposibles (09).

## 5. Huella de carbono (CodeCarbon, red eléctrica de Colombia: 259,5 g CO2eq/kWh)

| | Tiempo | Energía | Emisiones |
|---|---|---|---|
| **1 operación de Rope** (media de 91) | 0,8 s | 0,0016 Wh | **0,40 mg CO2eq** |
| **1 corrida de la suite de tests** | 18,4 s | 0,0285 Wh | **7,40 mg CO2eq** |
| **Experimento completo** (91 operaciones de Rope + 21 corridas de tests) | 7,5 min | 0,73 Wh | **0,19 g CO2eq** |

- **Verificar cuesta ~18 veces más que refactorizar.** El 80 % de la energía se fue en tests y el 19 % en Rope.
- **La huella de Rope es despreciable**, pero sin verificar no es seguro usarlo (11 de 19 rompen algo).
- **Limitaciones:** CodeCarbon **estima**, no mide. Sin `sudo` no hay acceso a `powermetrics`; usa `TDP × carga³` y 3 W fijos para la RAM.
  - La suite de tests (5,6 W) consume casi lo mismo que el equipo en reposo (5,7 W), así que la energía ≈ tiempo × potencia base.
  - CodeCarbon **no reconoció el Apple M4** y usaba 85 W en lugar de 20 W. Sin corregirlo, las cifras salían 2,6 veces más altas.

## 6. Lecciones metodológicas

- **La instalación editable (`pip install -e .`) contamina el experimento:** un módulo borrado en la copia se seguía importando desde el original. La refactorización 19 pasó en falso hasta que se desinstaló Tornado del entorno. El script ahora lo verifica al iniciar.
- **El oráculo tiene huecos:** `api_test` (que detectaría los cambios de API pública) solo corre en Linux. Además, una refactorización (16) puede hacer que se ejecuten menos tests sin que nada falle visiblemente.

## 7. Comparación entre los tres proyectos

| | PySnooper | Cookiecutter | Tornado |
|---|---|---|---|
| Tamaño | 964 líneas / 83 tests | 2806 / 379 | 25 996 / 1424 |
| Casos equivalentes que preservan (02–12) | 73 % | 73 % | 64 % |
| Inline | ✅ | ❌ cambia comportamiento | ❌ borra la función |
| Causa principal de los fallos | `locals()` | mocks por string | convenciones de nombres del framework; `async` |
| Huella de carbono | — | — | 0,4 mg/op. Rope; 7,4 mg/corrida de tests |
