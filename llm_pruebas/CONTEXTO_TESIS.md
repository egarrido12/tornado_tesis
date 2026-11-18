# Contexto del experimento Rope vs LLM en Tornado, para redactar la tesis

Resume lo que se hizo en el repositorio `tornado_tesis`, para que un asistente de redacción tenga el contexto sin acceso al código. Es el tercer proyecto del estudio; los anteriores son PySnooper (`~/PySnooper_tesis/llm_pruebas/CONTEXTO_TESIS.md`) y Cookiecutter (`~/cookiecutter_tesis/llm_pruebas/CONTEXTO_TESIS.md`). Los detalles están en `llm_pruebas/README.md` y `rope_pruebas/README.md`.

---

## 1. Qué se compara

- **Objeto de estudio:** Tornado, paquete `tornado/` (31 módulos de nivel superior, 25 062 líneas; unas 8 veces Cookiecutter).
- **Oráculo:** la suite de tests del proyecto (`python -m tornado.test.runtests`, `unittest`). Línea base: **1424 passed, 0 failed, 0 errors, 111 skipped** (de 1535). Una refactorización "preserva el comportamiento" si después pasan los mismos 1424 tests.
- **Rope** (1.15.0): 19 refactorizaciones elegidas por una persona. Las 02–12 reproducen los tipos y la numeración de PySnooper y Cookiecutter; las 13–20 son casos propios de Tornado (referencias en strings, doctests, verbos HTTP por `getattr`, rename de módulo, `await`).
- **LLM** (Claude **Sonnet 5.5**, no Opus como en Cookiecutter): recibe el **mismo prompt general** que en los otros proyectos (solo cambia el nombre) y decide qué refactorizar (2026-11-13).
- En ambos casos la refactorización se aplica sobre una **copia limpia**, se guarda el diff y se corre la suite. El código original nunca se modifica.
- **Novedad de Tornado:** cada fase se mide con **huella de carbono**, y la medición es **continua** (traza cada 0,1 s durante la ejecución), no solo el total al terminar.
- **Entorno:** Python 3.12.15, macOS (Apple M4), CodeCarbon 3.3.2 (offline, país `COL`, 259,5 g CO2eq/kWh). Tornado **no** se instala en el `.venv` (una instalación editable hacía pasar tests en falso).

## 2. Resultados de Rope (19 refactorizaciones)

| # | Tipo | Descripción | Tests (passed/failed/errors) | Veredicto |
|---|---|---|---|---|
| 02 | Rename | `httputil.url_concat` → `concat_url_args` | 1423 / 1 / 0 | **Rompe** (doctest) |
| 03 | Rename | `netutil.is_valid_ip` → `is_ip_address` | 1424 / 0 / 0 | Preserva |
| 04 | Rename | `BaseIOStream._maybe_add_error_listener` → `_ensure_error_listener` | 1424 / 0 / 0 | Preserva |
| 05 | Rename | clase `Configurable` → `ConfigurableBase` | 1419 / 4 / 1 | **Rompe** |
| 06 | Rename | parámetro `plus` de `url_escape` → `use_plus` | 1424 / 0 / 0 | Preserva |
| 07 | Extract | boundary de `parse_multipart_form_data` → `_unquote_boundary` | 1424 / 0 / 0 | Preserva |
| 08 | Extract | `_parse_request_range` → `_split_range_header` (2 salidas) | 1424 / 0 / 0 | Preserva |
| 09 | Extract | try/except con `return None` → `_parse_range_bounds` | — | **Rechazada por Rope** |
| 10 | Extract | bucle de `parse_body_arguments` → `_merge_urlencoded_arguments` | 1424 / 0 / 0 | Preserva |
| 11 | Inline | `_int_or_none` (reasigna su parámetro, 2 return) | 1401 / 23 / 0 | **Rompe** |
| 12 | Move | `tcpclient._format_addr` → `netutil` | 1424 / 0 / 0 | Preserva |
| 13 | Rename | `_try_inline_read` (parcheada por string con `mock.patch`) | 1421 / 0 / 3 | **Rompe** |
| 14 | Rename | `_normalize_header` (tiene un doctest) | 1423 / 1 / 0 | **Rompe** |
| 15 | Rename | igual que 14 con `docs=True` | 1424 / 0 / 0 | Preserva |
| 16 | Rename | `httputil.doctests` (nombrada como string en `TEST_MODULES`) | 1411 / 0 / 1 | **Rompe** |
| 17 | Rename | método `get` de `HelloHandler` (Tornado despacha con `getattr`) | 1423 / 1 / 0 | **Rompe** |
| 18 | Rename | `HelloHandler` (rutas por string) | 1423 / 0 / 1 | **Rompe** |
| 19 | Rename | módulo `locks` → `sync` (`__all__` lo nombra como string) | 1423 / 1 / 0 | **Rompe** |
| 20 | Extract | bloque con `await` de `RequestHandler._execute` | 0 / 0 / 1 | **Rompe** |

Totales: **8/19 preservan (42 %)**; en los casos equivalentes a PySnooper y Cookiecutter (02–12): **7/11 (64 %)**; 1 rechazo seguro (09). La mayoría de los fallos viene de referencias que el análisis estático no ve (strings, doctests, `getattr`); las excepciones son el bug del Inline (11) y el `await` (20). Esta corrida (2026-11-13) repitió el experimento con la medición continua y dio los mismos veredictos que la anterior.

## 3. Configuración del LLM

| Elemento | Valor |
|---|---|
| Modelo | `claude-sonnet-5-5` (Claude Sonnet 5.5, Anthropic) |
| SDK | `anthropic` 2.8.0, Messages API en modo streaming |
| Autenticación | API key en `ANTHROPIC_API_KEY` (no aparece en el código) |
| Effort / thinking | `high`; thinking adaptativo |
| `max_tokens` | 128 000 |
| Fallback de refusals | `fallbacks: "default"`; no se activó (las 24 respuestas son de `claude-sonnet-5-5`) |
| Caché de prompts | `cache_control: ephemeral` sobre el contexto (330 535 tokens) |
| Unidad de trabajo | Un módulo por llamada |
| Módulos | 8 de 31: `escape`, `netutil`, `locks`, `tcpclient`, `util`, `httputil`, `iostream`, `web` (los que tocan las pruebas de Rope; 40 % de las líneas) |
| Repeticiones | 3 por módulo = **24 llamadas** (+1 piloto) |
| Costo | **US$ 9.07** la ejecución principal; ~US$ 10 con el piloto (0.91) |
| Tiempo | 42–336 s por llamada (media 113 s) |
| Tokens | 510 429 de salida; 6 610 700 de entrada leídos de la caché; 1 322 140 escritos |

Por qué Sonnet y 8 módulos: con 330 000 tokens de contexto por llamada y módulos de hasta 4 255 líneas, el paquete completo con Opus habría excedido el presupuesto de tokens. **Los resultados no son comparables 1 a 1 con Cookiecutter** (otro modelo).

## 4. Resultados del LLM

- **Preservación: 24/24 corridas** (1424 tests, 0 fallos). Sin errores de sintaxis, truncamientos, rechazos ni fallback.
- **API pública:** ningún cambio de nombre ni firma. Solo desaparecen imports de `typing` sin uso (`Tuple` en `tcpclient`, `Optional` y `Type` en `locks`).
- **Determinismo:** los 8 módulos dieron 3 diffs distintos en 3 corridas. La estrategia es estable; cambian nombres, detalle y tamaño (`web`: +275 a +361 líneas).
- **Refactorizaciones elegidas:** sobre todo Extract Method (~100 puntos de extracción; `httputil` +9–10 funciones, `iostream` ~13, `web` ~15), además de Rename Variable, Guard Clauses, constantes simbólicas y Remove Dead Code. No usa Move ni Inline Function (un archivo por llamada).
- **Frente a los bloques donde Rope falló:** a diferencia de Cookiecutter, **el LLM evita los puntos conflictivos**: no elimina `_int_or_none` (11), no extrae `_parse_request_range` (08, 09) ni el bloque con `await` de `_execute` (20), y no renombra los privados que los tests parchean por nombre (13). Sí extrae los bloques "fáciles" (urlencoded, multipart) que Rope también resolvió (07, 10). **No demuestra que detecte referencias en strings:** el modelo no veía los tests.
- **Un incidente:** un `ReadTimeout` en `netutil_run2` provocó 1 reintento automático.
- **Costo evitable:** hubo 4 escrituras de caché (≈ US$ 0.83 cada una) en vez de 1, porque la caché dura 5 minutos y las llamadas de `web` duran más. Con `ttl: "1h"` se habrían ahorrado unos US$ 2.5.

## 5. Huella de carbono

**Cómo se mide.** CodeCarbon calcula la energía de una *task* una sola vez, al terminar. Se agregó `rope_pruebas/carbono_traza.py`, que muestrea la carga de CPU de todo el equipo cada 0,1 s durante cada fase y calcula la potencia con `P = TDP × (0,1 + 0,9 × carga³)` (TDP 20 W para el M4) + 3 W de RAM. La traza (`traza_carbono.csv`) coincide con CodeCarbon (≈ 1–2 %).

| | Rope | LLM (Sonnet 5.5) |
|---|---|---|
| Fases medidas | 91 operaciones + 21 corridas de tests + análisis | 24 llamadas + 25 corridas de tests |
| Energía total | 0,631 Wh | 4,73 Wh (llamadas) + 0,64 Wh (tests) |
| Emisiones | 0,164 g CO2eq | 1,23 g (llamadas) + 0,17 g (tests) |
| Una operación | 0,70 s, 0,0011 Wh, 0,28 mg | 42–336 s, 0,06–0,47 Wh locales |
| Una corrida de tests | 18,4 s, 0,0265 Wh, 6,9 mg | 19 s, ~0,027 Wh |

**Interpretación:**
1. **La energía local del LLM es la del equipo en espera.** La potencia media durante las llamadas fue 5,0–5,1 W, igual que en reposo (5,0 W): el Mac solo espera por red. El consumo real del LLM está en los servidores de Anthropic y **no es medible desde aquí**; por eso se registran los tokens.
2. **Los tests casi no se distinguen del reposo en potencia** (~5,05 W): la suite usa un solo hilo y el modelo cúbico de CodeCarbon apenas sube con una carga baja. La energía de cada fase es, sobre todo, **duración × potencia base**.
3. **Verificar cuesta más que refactorizar:** con Rope la suite es el 84 % de la energía del experimento y una corrida emite ~25 veces más que una operación de Rope.
4. Las operaciones de Rope de menos de 0,1 s (07, 08, 10, 09) no dejan ninguna muestra de la traza.

**Limitaciones:** (a) potencia **estimada** por carga de CPU (sin `sudo` no hay `powermetrics`); (b) otro proyecto (`black_tesis`) corría actividad en el mismo Mac durante el experimento y la medición es de todo el equipo; hay picos aislados de hasta 23 W en la fase de espera del LLM, que no deben atribuirse al modelo, aunque la potencia media apenas cambia; (c) sin medición del lado del servidor; (d) con el TDP genérico de 85 W de CodeCarbon, Rope habría reportado 2,3 veces más (se fuerza 20 W).

## 6. Comparación

| Criterio | Rope | LLM (Sonnet 5.5) |
|---|---|---|
| Preservación | 8/19 (42 %); 7/11 en los casos equivalentes | **24/24 (100 %)** |
| Quién decide | La persona | El modelo |
| Alcance de cada cambio | Pequeño (1 operación) | Grande (hasta +361 líneas en `web`) |
| Tiempo | < 1 s | 42–336 s |
| Costo | Gratis | US$ 0.11–1.5 por corrida (US$ 9.07) |
| Revisabilidad | Diff mínimo | Diff grande, requiere revisión |

**Comparación entre proyectos:**

| | PySnooper | Cookiecutter | Tornado |
|---|---|---|---|
| Tamaño | 964 líneas | 2 806 | 25 062 |
| Rope: casos equivalentes que preservan | 8/11 | 8/11 | 7/11 |
| Rope: casos propios que preservan | — | 0/3 | 1/8 (solo el 15, con `docs=True`) |
| LLM: modelo | Opus 5.5 | Opus 5.5 | **Sonnet 5.5** |
| LLM: corridas que preservan | 15/15 | 51/51 | 24/24 |
| LLM: costo | US$ 2.55 | US$ 6.80 | US$ 9.07 |
| LLM: ¿extrajo los bloques donde Rope falló? | Sí | Sí | **No: los evitó** |

## 7. Limitaciones y amenazas a la validez

1. Los tests son el único oráculo (111 omitidos).
2. Alcance parcial: 8 de 31 módulos.
3. Un modelo (distinto al de Cookiecutter) y un prompt.
4. 3 corridas por módulo: 24/24 no descarta una tasa baja de error.
5. Comparación no simétrica: Rope hizo 19 operaciones elegidas (varias para romperlo); el LLM eligió las suyas.
6. La lista de refactorizaciones la escribe el propio modelo; el conteo es aproximado.
7. El modelo no veía los tests.
8. La medición de carbono es estimada y con ruido ajeno (sección 5).
