# Resumen de pruebas con Rope (Tornado)

- Python: `3.12.15`
- Rope: `1.15.0`
- CodeCarbon: `3.3.2` (modo offline, país `COL`, CPU `Apple M4` TDP 20.0 W, RAM 3.0 W)
- Fecha: 2026-10-30 10:31

## Línea base

1535 tests: 1424 passed, 0 failed, 111 skipped, 0 errors

## Refactorizaciones

| # | Tipo | Descripción | Rope | Tiempo Rope (s, media de 5) | Tests (passed/failed/errors) | Veredicto |
|---|---|---|---|---|---|---|
| 02_rename_funcion | Rename | httputil.url_concat -> concat_url_args (usada en auth, httpclient y tests) | aplicada | 1.061 | 1423 / 1 / 0 | **ROMPE TESTS** |
| 03_rename_funcion_importada | Rename | netutil.is_valid_ip -> is_ip_address (también importada por caresresolver y los tests) | aplicada | 1.043 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |
| 04_rename_metodo | Rename | BaseIOStream._maybe_add_error_listener -> _ensure_error_listener | aplicada | 1.13 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |
| 05_rename_clase | Rename | util.Configurable -> ConfigurableBase (clase base de IOLoop, AsyncHTTPClient y Resolver) | aplicada | 0.793 | 1419 / 4 / 1 | **ROMPE TESTS** |
| 06_rename_parametro | Rename | parámetro plus de escape.url_escape -> use_plus (los llamadores lo pasan por nombre) | aplicada | 0.646 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |
| 07_extract_boundary | Extract Method | quitar comillas del boundary en parse_multipart_form_data -> _unquote_boundary | aplicada | 0.181 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |
| 08_extract_rango | Extract Method | separar unidad y valor en _parse_request_range -> _split_range_header (2 valores de salida) | aplicada | 0.035 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |
| 09_extract_con_return | Extract Method | try/except con `return None` de _parse_request_range -> _parse_range_bounds (caso límite) | error: RefactoringError: Return should be the last statement. | 0.007 | — | **RECHAZADA POR ROPE** |
| 10_extract_bucle | Extract Method | bucle que copia argumentos urlencoded en parse_body_arguments -> _merge_urlencoded_arguments | aplicada | 0.033 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |
| 11_inline_funcion | Inline | inline de httputil._int_or_none en _parse_request_range (2 llamadas; reasigna su parámetro y tiene 2 return) | aplicada | 0.506 | 1401 / 23 / 0 | **ROMPE TESTS** |
| 12_move_funcion | Move | mover tcpclient._format_addr a netutil (los tests la importan) | aplicada | 1.141 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |
| 13_rename_parcheada | Rename | BaseIOStream._try_inline_read -> _read_inline_if_possible (los tests la parchean con mock.patch("tornado.iostream.BaseIOStream._try_inline_read")) | aplicada | 0.966 | 1421 / 0 / 3 | **ROMPE TESTS** |
| 14_rename_con_doctest | Rename | httputil._normalize_header -> _to_header_case (tiene un doctest en su docstring) | aplicada | 0.767 | 1423 / 1 / 0 | **ROMPE TESTS** |
| 15_rename_con_doctest_docs | Rename | igual que 14 pero con docs=True | aplicada | 0.756 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |
| 16_rename_en_test_modules | Rename | httputil.doctests -> doctest_suite (runtests.TEST_MODULES la nombra como string) | aplicada | 0.662 | 1411 / 0 / 1 | **ROMPE TESTS** |
| 17_rename_verbo_http | Rename | método get de HelloHandler -> handle_get (Tornado despacha con getattr(self, método_http)) | aplicada | 1.921 | 1423 / 1 / 0 | **ROMPE TESTS** |
| 18_rename_handler_string | Rename | clase HelloHandler -> GreetingHandler (las rutas la nombran como string "tornado.test.web_test.HelloHandler") | aplicada | 1.141 | 1423 / 0 / 1 | **ROMPE TESTS** |
| 19_rename_modulo | Rename (módulo) | módulo tornado/locks.py -> tornado/sync.py (tornado.__all__ lo nombra como string) | aplicada | 1.206 | 1423 / 1 / 0 | **ROMPE TESTS** |
| 20_extract_await | Extract Method | bloque con `await` de RequestHandler._execute (async def) -> _run_prepare | aplicada | 0.603 | 0 / 0 / 1 | **ROMPE TESTS** |

## Huella de carbono (CodeCarbon)

| Experimento | Fase | Duración (s) | Energía (Wh) | Emisiones (mg CO2eq) |
|---|---|---|---|---|
| 00_reposo | reposo | 20.006 | 0.0316 | 8.205 |
| 00_linea_base | tests (media de 3) | 18.420 | 0.0285 | 7.403 |
| 01_analisis | analisis | 1.902 | 0.0043 | 1.104 |
| 02_rename_funcion | rope (media de 5) | 1.061 | 0.0024 | 0.620 |
| 02_rename_funcion | tests | 18.965 | 0.0304 | 7.893 |
| 03_rename_funcion_importada | rope (media de 5) | 1.043 | 0.0022 | 0.578 |
| 03_rename_funcion_importada | tests | 18.647 | 0.0288 | 7.463 |
| 04_rename_metodo | rope (media de 5) | 1.130 | 0.0039 | 1.017 |
| 04_rename_metodo | tests | 19.266 | 0.0382 | 9.925 |
| 05_rename_clase | rope (media de 5) | 0.793 | 0.0014 | 0.355 |
| 05_rename_clase | tests | 18.884 | 0.0316 | 8.202 |
| 06_rename_parametro | rope (media de 5) | 0.646 | 0.0010 | 0.252 |
| 06_rename_parametro | tests | 18.542 | 0.0286 | 7.413 |
| 07_extract_boundary | rope (media de 5) | 0.181 | 0.0003 | 0.073 |
| 07_extract_boundary | tests | 18.356 | 0.0305 | 7.906 |
| 08_extract_rango | rope (media de 5) | 0.035 | 0.0000 | 0.013 |
| 08_extract_rango | tests | 18.789 | 0.0296 | 7.685 |
| 09_extract_con_return | rope | 0.007 | 0.0000 | 0.003 |
| 10_extract_bucle | rope (media de 5) | 0.033 | 0.0000 | 0.012 |
| 10_extract_bucle | tests | 18.632 | 0.0299 | 7.751 |
| 11_inline_funcion | rope (media de 5) | 0.506 | 0.0008 | 0.216 |
| 11_inline_funcion | tests | 18.754 | 0.0299 | 7.749 |
| 12_move_funcion | rope (media de 5) | 1.141 | 0.0021 | 0.548 |
| 12_move_funcion | tests | 18.296 | 0.0267 | 6.929 |
| 13_rename_parcheada | rope (media de 5) | 0.966 | 0.0019 | 0.484 |
| 13_rename_parcheada | tests | 19.015 | 0.0304 | 7.880 |
| 14_rename_con_doctest | rope (media de 5) | 0.767 | 0.0016 | 0.423 |
| 14_rename_con_doctest | tests | 18.838 | 0.0296 | 7.686 |
| 15_rename_con_doctest_docs | rope (media de 5) | 0.756 | 0.0012 | 0.324 |
| 15_rename_con_doctest_docs | tests | 18.765 | 0.0296 | 7.672 |
| 16_rename_en_test_modules | rope (media de 5) | 0.662 | 0.0011 | 0.288 |
| 16_rename_en_test_modules | tests | 18.714 | 0.0300 | 7.790 |
| 17_rename_verbo_http | rope (media de 5) | 1.921 | 0.0035 | 0.897 |
| 17_rename_verbo_http | tests | 18.368 | 0.0261 | 6.775 |
| 18_rename_handler_string | rope (media de 5) | 1.141 | 0.0020 | 0.522 |
| 18_rename_handler_string | tests | 18.770 | 0.0264 | 6.859 |
| 19_rename_modulo | rope (media de 5) | 1.206 | 0.0018 | 0.471 |
| 19_rename_modulo | tests | 18.889 | 0.0264 | 6.861 |
| 20_extract_await | rope (media de 5) | 0.603 | 0.0009 | 0.234 |
| 20_extract_await | tests | 0.220 | 0.0003 | 0.079 |

### Totales

| Concepto | Duración (s) | Energía (Wh) | Emisiones (mg CO2eq) |
|---|---|---|---|
| Todas las operaciones de Rope (91) | 72.95 | 0.1411 | 36.630 |
| Análisis estático | 1.90 | 0.0043 | 1.104 |
| Todas las corridas de tests | 373.97 | 0.5885 | 152.729 |
| **Experimento completo** (sin reposo) | 448.82 | 0.7339 | 190.462 |

- Reposo (20 s sin carga): potencia media 5.69 W.
- Factor de emisión usado: 259.5 g CO2eq/kWh.
- Sensibilidad: con el TDP genérico de 85 W que CodeCarbon usa por defecto en este equipo, el experimento completo habría reportado 1.9037 Wh y 494.020 mg CO2eq.
- Una operación de Rope: media 0.802 s, 0.0016 Wh, 0.403 mg CO2eq (desv. 0.362 mg).
- Una corrida de la suite (línea base): media 18.42 s, 0.0285 Wh, 7.403 mg CO2eq (desv. 0.529 mg).
