# Pruebas de Tornado con un LLM (prompt general)

Este documento describe el proceso completo: qué se probó, cómo reproducirlo, qué resultados se obtuvieron, cómo interpretarlos y cómo se comparan con las pruebas de Rope (`../rope_pruebas/`). Es una réplica del experimento hecho sobre PySnooper y Cookiecutter (`~/cookiecutter_tesis/llm_pruebas/`), con dos diferencias: el modelo es **Claude Sonnet 5.5** (más barato, para ajustarse al presupuesto de tokens) y cada fase se mide con **huella de carbono en continuo** (sección 5).

- **Proyecto bajo prueba:** Tornado, carpeta `tornado/` (25 062 líneas en 31 módulos de nivel superior).
- **Modelo:** Claude Sonnet 5.5 (`claude-sonnet-5-5`), effort `high`, API de Anthropic (SDK `anthropic` 2.8.0).
- **Entorno:** Python 3.12.15, suite de Tornado con `unittest`, macOS (Apple M4), `.venv`.
- **Fecha de ejecución:** 2026-11-13.
- **Ejecución principal:** `resultados/20261113_095421/` (24 corridas: 8 módulos × 3).
- **Piloto:** `resultados/20261113_094427/` (1 corrida de `escape`; sirvió para validar el flujo y el medidor de carbono).

---

## 1. Objetivo y diferencia con Rope

La pregunta es: **cuando un LLM refactoriza Tornado por su cuenta, ¿conserva el comportamiento? ¿Qué refactorizaciones elige? ¿Cuánto consume?**

| | Rope | LLM |
|---|---|---|
| ¿Quién decide qué refactorizar? | La persona (offset + nombre nuevo) | **El modelo** |
| ¿Quién ejecuta el cambio? | Rope | El modelo |
| Instrucción | Una refactorización concreta por prueba (19 en total) | **Un único prompt general**, igual para todos los módulos |
| Determinismo | Total | No: el mismo prompt puede dar resultados distintos |

## 2. Metodología

1. **Prompt fijo y versionado:** [`prompt_v1.md`](prompt_v1.md), idéntico al de PySnooper y Cookiecutter salvo por el nombre del proyecto. Pide mejorar legibilidad y mantenibilidad sin cambiar el comportamiento, con estas reglas: no cambiar nombres ni firmas públicas, no agregar funcionalidades ni dependencias, modificar solo el archivo indicado y mantener la compatibilidad con las versiones de Python soportadas. Pide devolver el archivo completo y una lista de las refactorizaciones aplicadas según el catálogo de Fowler.
2. **Contexto:** en cada llamada el modelo recibe **los 31 módulos de `tornado/*.py`** (330 535 tokens) como contexto de solo lectura, más la instrucción `Refactoriza el archivo tornado/<modulo>.py`. No incluye `tornado/test/` ni `tornado/platform/`. El contexto es idéntico en todas las llamadas, así que se reutiliza la caché de prompts.
3. **Unidad de trabajo:** un módulo por llamada.
4. **Repeticiones:** 3 corridas por módulo.
5. **Evaluación**, igual que con Rope: se aplica el archivo devuelto sobre una **copia limpia**, se genera el diff y se corre la suite completa (`python -m tornado.test.runtests`, 1535 tests). Si pasan los mismos 1424 tests que en la línea base, sin fallos ni errores, el veredicto es **comportamiento preservado**.
6. **Verificación de la API pública** con `ast`: se comparan, antes y después, los nombres públicos de nivel de módulo y las firmas de funciones y métodos públicos.
7. **Medición de carbono** de cada llamada y de cada corrida de tests (sección 5).

> El código original en `tornado/` **nunca se modifica**. Cada ejecución se guarda en su propia carpeta `resultados/<fecha_hora>/`.

### 2.1 Alcance: 8 de 31 módulos

Con 330 000 tokens de contexto por llamada y módulos de hasta 4 255 líneas (`web`), el paquete completo habría salido caro. Se eligieron los **8 módulos que tocan las pruebas de Rope (02–20)**, que son los que se pueden comparar: `escape`, `netutil`, `locks`, `tcpclient`, `util`, `httputil`, `iostream` y `web`. Suman 10 020 líneas (40 % del paquete). Los otros 23 módulos no se probaron.

### 2.2 Incidencias durante la ejecución

- **Un corte de red:** `netutil_run2` recibió un `ReadTimeout` y el script reintentó tras 30 s (reintento automático, como en Cookiecutter). La corrida registrada es una respuesta completa (`stop_reason = end_turn`). La llamada interrumpida no queda en el resumen, así que su costo, si lo hubo, no está contado. La corrida duró 756 s de reloj frente a unos 80 s de las otras dos.
- **Otro experimento en paralelo:** durante la ejecución corría en el mismo Mac el experimento de `black_tesis`. Afecta a la medición de carbono (sección 5.4), no a los tests ni a las respuestas del modelo.

## 3. Cómo ejecutarlo

Requiere una API key de Anthropic en `ANTHROPIC_API_KEY` (en este equipo está en `~/.zshrc`) y que **tornado no esté instalado** en el `.venv` (el script aborta si lo está; ver `../rope_pruebas/README.md`).

```bash
# ver el prompt y contar los tokens de entrada, sin generar nada
.venv/bin/python llm_pruebas/ejecutar_pruebas_llm.py --dry-run

# piloto barato (~US$ 0.9, casi todo es escribir la caché)
.venv/bin/python llm_pruebas/ejecutar_pruebas_llm.py --modulos escape --corridas 1

# ejecución completa (8 módulos × 3 corridas, ~65 min, ~US$ 9)
caffeinate -dimsu .venv/bin/python llm_pruebas/ejecutar_pruebas_llm.py

# continuar una ejecución interrumpida
.venv/bin/python llm_pruebas/ejecutar_pruebas_llm.py --reanudar 20261113_095421

# variantes
.venv/bin/python llm_pruebas/ejecutar_pruebas_llm.py --modulos web --corridas 5
.venv/bin/python llm_pruebas/ejecutar_pruebas_llm.py --modelo claude-opus-5-5
```

**Recomendaciones:** dejar el equipo conectado, lanzar con `caffeinate -dimsu` y **no correr nada más en el Mac** mientras se mide el carbono.

### Estructura de archivos

```
llm_pruebas/
├── README.md                  ← este documento
├── CONTEXTO_TESIS.md          ← resumen para redactar la tesis
├── ejecutar_pruebas_llm.py    ← script que automatiza todo
├── prompt_v1.md               ← prompt general (versionado)
├── .gitignore                 ← ignora _trabajo/
├── _trabajo/                  ← copias del proyecto, una por corrida (temporal, se puede borrar)
└── resultados/
    └── <fecha_hora>/
        ├── resumen.md / resumen.json       ← tabla general, API, tokens, costo, determinismo, carbono
        ├── prompt.md                       ← copia del prompt usado
        ├── traza_carbono.csv               ← potencia cada 0,1 s durante cada fase
        ├── 00_linea_base_tests.txt
        ├── <modulo>_run<n>_respuesta.md    ← respuesta completa del modelo (incluye su lista de refactorizaciones)
        ├── <modulo>_run<n>.py              ← archivo refactorizado
        ├── <modulo>_run<n>.diff            ← diff contra el original
        └── <modulo>_run<n>_tests.txt       ← salida de la suite con ese archivo
```

La medición de carbono vive en [`../rope_pruebas/carbono_traza.py`](../rope_pruebas/carbono_traza.py) y la comparten los dos experimentos.

---

## 4. Resultados

### 4.1 Línea base

`1535 tests ejecutados: 1424 passed, 0 failed, 0 errors, 111 skipped`, idéntica a la de Rope.

### 4.2 Preservación del comportamiento: 24 de 24

| Módulo | Líneas | Tests en las 3 corridas | +/− líneas (rango) | Tiempo medio de la llamada | Costo (3 corridas) |
|---|---|---|---|---|---|
| `escape` | 411 | 1424 / 0 / 0 ✅✅✅ | +58…66 / −42…48 | 44 s | US$ 1.13 * |
| `netutil` | 689 | 1424 / 0 / 0 ✅✅✅ | +121…136 / −82…97 | 82 s | US$ 1.30 * |
| `locks` | 582 | 1424 / 0 / 0 ✅✅✅ | +45…50 / −34…40 | 52 s | US$ 0.36 |
| `tcpclient` | 389 | 1424 / 0 / 0 ✅✅✅ | +95…130 / −56…72 | 47 s | US$ 0.35 |
| `util` | 559 | 1424 / 0 / 0 ✅✅✅ | +45…58 / −21…33 | 55 s | US$ 0.41 |
| `httputil` | 1441 | 1424 / 0 / 0 ✅✅✅ | +184…193 / −137…154 | 143 s | US$ 0.85 |
| `iostream` | 1694 | 1424 / 0 / 0 ✅✅✅ | +219…283 / −163…218 | 155 s | US$ 1.00 |
| `web` | 4255 | 1424 / 0 / 0 ✅✅✅ | +275…361 / −189…260 | 326 s | US$ 3.68 * |
| **Total** | **10 020** | **24 / 24 preservan** | | **113 s** (42–336 s) | **US$ 9.07** |

\* Incluyen una o dos escrituras de caché de 330 535 tokens (≈ US$ 0.83 cada una); ver la nota de costos.

- No hubo errores de sintaxis, respuestas truncadas, rechazos ni fallback a otro modelo: las 24 respuestas son de `claude-sonnet-5-5` con `stop_reason = end_turn`. La respuesta más larga (`web`, ~67 000 tokens de salida) cabe en el `max_tokens` de 128 000.
- **Tokens:** 510 429 de salida (incluye el razonamiento interno), 6 610 700 de entrada leídos de la caché, 1 322 140 escritos en la caché y 612 de entrada sin caché.
- **Nota de costos.** La caché de prompts dura 5 minutos. Las 4 escrituras de caché (`escape_run1`, `netutil_run2`, `web_run2` y `web_run3`) pasaron cada una de ≈ US$ 0.1–0.4 a ≈ US$ 1. Eso son unos **US$ 2.5 evitables**: con `cache_control: {type: ephemeral, ttl: "1h"}` las corridas largas de `web` (> 5 min) no la habrían perdido. El piloto costó US$ 0.91 aparte. **Total aproximado del experimento: US$ 10.**

Detalle por corrida: [`resultados/20261113_095421/resumen.md`](resultados/20261113_095421/resumen.md).

### 4.3 Refactorizaciones elegidas por el modelo

Clasificación a partir de la lista que el modelo entrega al final de cada respuesta (conteo aproximado: varias respuestas combinan tipos).

| Tipo | Apariciones (de 24 respuestas) |
|---|---|
| Extract Method / Extract Function | ~100 puntos de extracción (en todas las respuestas) |
| Rename Variable | 10 |
| Replace Nested Conditional with Guard Clauses | 9 |
| Replace Magic Number / Literal with Symbolic Constant | 9 |
| Remove Dead Code | 6 |

Lo que se ve en los diffs:

- **Extract Method es la refactorización principal.** `httputil` gana 9–10 funciones privadas nuevas (`_parse_query_arguments`, `_parse_urlencoded_body`, `_parse_multipart_body`, `_reject_content_encoding`…), `iostream` unas 13 y `web` unas 15–17 (`_collect_module_resources`, `_validate_cookie_attributes`, `_resolve_byte_range`, `_apply_debug_settings`…).
- **Elimina duplicación:** en `web`, seis bloques repetidos de `html.index(...)` + concatenación pasan a una sola función `_insert_before` o equivalente.
- **Mantiene los nombres públicos y también casi todos los privados** que ya existían: `_maybe_add_error_listener`, `_try_inline_read`, `_format_addr`, `_int_or_none`, `_normalize_header` y `_parse_request_range` siguen con su nombre original en las 3 corridas.
- Igual que en PySnooper y Cookiecutter, **no usa Move ni Inline Function**: el prompt limita los cambios a un archivo.

### 4.4 Determinismo

| Módulo | Corridas | Diffs distintos |
|---|---|---|
| los 8 módulos | 3 | **3** |

Ninguna corrida produjo un diff idéntico a otra. La estrategia es estable (en `httputil` las tres extraen el cuerpo urlencoded, el multipart y el rechazo de `Content-Encoding`) y lo que cambia son los nombres, el grado de detalle y el tamaño (`web`: +275 a +361 líneas).

### 4.5 Respeto de la API pública (verificación automática con `ast`)

| Cambio detectado | Corridas | ¿Rompe algo? |
|---|---|---|
| Eliminado `import Tuple` (`tcpclient`) | 3/3 | No: deja de usarse al pasar a `tuple[...]` |
| Eliminados `import Optional` e `import Type` (`locks`) | 2/3 | No, por la misma razón |

Ningún nombre público ni firma cambió en las 24 corridas. El único efecto es que desaparecen imports de `typing` que otros módulos podrían haber importado desde ahí (nada en Tornado lo hace: los 1424 tests pasan).

---

## 5. Huella de carbono

### 5.1 Qué se mide y cómo

Se usa **CodeCarbon 3.3.2** en modo offline (país `COL`) más un **muestreador propio** (`carbono_traza.py`). Hay un cambio respecto de las pruebas anteriores: CodeCarbon, dentro de una *task*, calcula la energía **una sola vez, al terminar** (con la carga media de un monitor de 1 s). Eso da el total, pero no muestra qué pasó durante la ejecución. Ahora, mientras corre cada fase, un hilo lee la carga de CPU del equipo **cada 0,1 s** y calcula la potencia instantánea:

```
P_cpu = TDP × (0.1 + 0.9 × carga³)     (TDP = 20 W para el Apple M4)
P_ram = 3 W                            (constante de CodeCarbon)
```

La energía es la integral de esas muestras, y cada muestra se guarda en `traza_carbono.csv` (36 345 filas en esta ejecución) para poder graficar la curva. La traza coincide con CodeCarbon: **4.731 Wh frente a 4.788 Wh** en las llamadas al LLM y **0.641 Wh frente a 0.651 Wh** en los tests (diferencia ≈ 1 %).

Las fases medidas son: reposo (20 s), línea base, y por cada corrida **`llm`** (la llamada a la API) y **`tests`**.

### 5.2 Resultados

| Fase | n | Duración total | Energía (traza) | Emisiones |
|---|---|---|---|---|
| Llamadas al LLM (espera local) | 24 | 3 386 s | 4.731 Wh | 1 228 mg CO2eq |
| Corridas de tests | 24 | 457 s | 0.641 Wh | 166 mg CO2eq |

- Por módulo (suma de 3 corridas, llamadas al LLM): `escape` 0.18 Wh, `locks` 0.22, `tcpclient` 0.20, `util` 0.23, `httputil` 0.60, `iostream` 0.65, `web` 1.36, `netutil` 1.29 (inflada por el corte de red: 756 s en una sola corrida).
- Una corrida de la suite de tests: 0.026–0.028 Wh y ~19 s en todas las corridas.
- Reposo: 5.0 W de media.

### 5.3 Qué significan estos números

1. **La energía local de la llamada al LLM es el consumo en reposo del equipo.** La potencia media durante las llamadas fue de **5.0–5.1 W**, igual que en reposo (5.0 W). Mientras el modelo trabaja, el Mac solo espera por la red, así que 3 386 s × 5.0 W = 4.70 Wh de los 4.73 Wh medidos son simple espera. El consumo **real** del LLM está en los servidores de Anthropic y **no se puede medir desde aquí**. Por eso se guardan los tokens (510 429 de salida) como indicador de la carga que se le pidió al modelo.
2. **Los tests casi no se distinguen del reposo en potencia** (5.0–5.3 W de media): la suite de Tornado es de un solo hilo y la carga del equipo (10 núcleos) es baja. Con la fórmula cúbica del modelo de CodeCarbon, una carga de ~12 % apenas sube la potencia. Las diferencias de energía entre fases son, sobre todo, **diferencias de duración**.
3. **Rope vs LLM en el equipo local:** una operación de Rope dura 0.7 s y consume 0.0011 Wh (0.28 mg CO2eq); una llamada al LLM dura 42–336 s y consume 0.06–0.47 Wh locales, además de lo que gaste el servidor. Pero la comparación justa incluye los tests (~19 s por verificación): con Rope, la suite es el 96 % del tiempo de máquina de una refactorización verificada; con el LLM, solo el 14 % (la espera de la llamada domina).

### 5.4 Limitaciones de la medición

- **Otro experimento corría en paralelo** (`black_tesis`). La medición es de todo el equipo (`tracking_mode='machine'`). Se nota en picos aislados de **23 W** (una sola muestra de 0,1 s) en `tcpclient_run1/2`, `iostream_run3`, `web_run1` y `web_run3`, y de 12–15 W en otras. Como son muestras sueltas, la potencia media apenas cambia (5.0–5.1 W en todas las corridas), pero los **picos de la traza no deben atribuirse al modelo**. Para cifras limpias, repetir sin procesos ajenos.
- **La potencia es una estimación por carga de CPU** (sin `sudo` no hay `powermetrics` en macOS). No incluye GPU ni el consumo real del chip. Sirve para comparar fases entre sí, no como medida absoluta.
- **No hay medición del lado del servidor.** La huella de carbono de generar los 510 429 tokens no está incluida.
- **Factor de emisión:** 259.5 g CO2eq/kWh (red de Colombia, tabla de CodeCarbon).

---

## 6. Comparación con Rope

### 6.1 Resumen

| Criterio | Rope | LLM (Sonnet 5.5) |
|---|---|---|
| Preservación del comportamiento | 8/19 (42 %); 7/11 en los casos equivalentes a PySnooper y Cookiecutter | **24/24 corridas (100 %)** |
| Decide qué refactorizar | No | Sí |
| Determinismo | Total | Estrategia estable, texto variable (3/3 diffs distintos) |
| Alcance de cada cambio | Pequeño y acotado (1 operación) | Grande (hasta +361 líneas en `web`) |
| Cambios en varios archivos | Sí (no ve strings) | No en este diseño (un archivo por llamada) |
| Tiempo | < 1 s por refactorización | 42–336 s por corrida |
| Costo | Gratis | US$ 0.11–1.5 por corrida (US$ 9.07 en total) |
| Revisabilidad | Diff mínimo y predecible | Diff grande, requiere revisión humana |

### 6.2 Por qué fallan las refactorizaciones de Rope y no las del LLM

Los fallos de Rope en Tornado (02, 05, 11, 13, 14, 16–20) vienen en su mayoría (todos salvo 11 y 20) de **referencias que el análisis estático no ve**: `mock.patch("tornado.iostream.BaseIOStream._try_inline_read")`, handlers por string, `__all__` perezoso, doctests, método `get` despachado con `getattr`. El LLM **no tuvo ese problema, pero por una razón distinta**: el prompt le prohíbe renombrar nombres públicos y el modelo **tampoco renombró los privados que los tests usan por nombre** (`_try_inline_read`, `_normalize_header`, `_maybe_add_error_listener`…). El experimento **no demuestra que el LLM detecte referencias en strings**: el modelo no veía los tests.

### 6.3 Mismos bloques que Rope

| Bloque | Rope | LLM (3 corridas) |
|---|---|---|
| `parse_body_arguments`: bucle de argumentos urlencoded (10) | ✅ preserva | Extrae `_parse_urlencoded_body` / `_parse_query_arguments` ✅ 3/3 |
| `parse_multipart_form_data`: manejo del boundary (07) | ✅ preserva | Extrae `_parse_multipart_body` y partes ✅ 3/3 |
| `_parse_request_range` (08, 09) | ✅ / ⛔ rechazada | **No la extrae**: la deja igual |
| `_int_or_none` (11, Inline) | ❌ 1401 / 23 | **No la elimina** ✅ 3/3 |
| `RequestHandler._execute` con `await` (20) | ❌ error | Extrae otros bloques de `web`; no el de `prepare()` (en las 3 corridas) |
| `_format_addr` (12, Move) | ✅ preserva | No la mueve (un archivo por llamada); la conserva ✅ 3/3 |

Es decir, a diferencia de Cookiecutter (donde el LLM extrajo justo los bloques donde Rope falló), aquí el LLM **evita los puntos conflictivos**: no toca `_int_or_none`, `_parse_request_range` ni el bloque con `await`.

---

## 7. Limitaciones y amenazas a la validez

1. **Los tests son el único oráculo.** Pasar 1424 tests no demuestra equivalencia. Hay 111 tests omitidos (dependencias opcionales y plataformas) y las zonas que esos tests cubren no se verificaron.
2. **Alcance parcial:** 8 de 31 módulos (40 % de las líneas). Quedan fuera `httpclient`, `websocket`, `ioloop`, `gen`, `http1connection`, etc.
3. **Un solo modelo, un solo prompt.** Los resultados corresponden a `claude-sonnet-5-5`, effort `high` y `prompt_v1.md`. No son comparables 1 a 1 con Cookiecutter (Opus 5.5).
4. **3 corridas por módulo** bastan para ver variabilidad, no para estimar una tasa de error: 24/24 no descarta una tasa baja pero no nula.
5. **Diffs grandes.** En `web` el LLM cambia unas 600 líneas por corrida; si algo fallara, aislar la causa sería difícil.
6. **Comparación no simétrica.** Rope recibió 19 operaciones elegidas por una persona, varias a propósito para romperlo. El LLM eligió las suyas.
7. **La lista de refactorizaciones la escribe el propio modelo;** el conteo de la sección 4.3 es aproximado.
8. **El modelo no veía los tests** (sección 6.2).
9. **Carbono:** ver la sección 5.4 (experimento paralelo, potencia estimada, sin medición del servidor).

## 8. Próximos pasos posibles

- Repetir la parte de carbono con el equipo en reposo, sin otros procesos.
- Repetir con otros modelos (Opus 5.5, para comparar directamente con Cookiecutter).
- Un prompt con los tests en el contexto y permiso para cambios públicos, para comparar con los Rename 13–19 de Rope.
- Ampliar a los módulos que faltan.
- Usar `cache_control` con `ttl: "1h"` para evitar las escrituras de caché repetidas.
