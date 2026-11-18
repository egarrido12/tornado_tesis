# Resumen de pruebas con Rope (Tornado)

- Python: `3.12.15`
- Rope: `1.15.0`
- CodeCarbon: `3.3.2` (modo offline, país `COL`, CPU `Apple M4` TDP 20.0 W, RAM 3.0 W)
- Fecha: 2026-11-13 09:54

## Línea base

1535 tests: 1424 passed, 0 failed, 111 skipped, 0 errors

## Refactorizaciones

| # | Tipo | Descripción | Rope | Tiempo Rope (s, media de 5) | Tests (passed/failed/errors) | Veredicto |
|---|---|---|---|---|---|---|
| 02_rename_funcion | Rename | httputil.url_concat -> concat_url_args (usada en auth, httpclient y tests) | aplicada | 1.061 | 1423 / 1 / 0 | **ROMPE TESTS** |
| 03_rename_funcion_importada | Rename | netutil.is_valid_ip -> is_ip_address (también importada por caresresolver y los tests) | aplicada | 0.791 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |
| 04_rename_metodo | Rename | BaseIOStream._maybe_add_error_listener -> _ensure_error_listener | aplicada | 1.186 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |
| 05_rename_clase | Rename | util.Configurable -> ConfigurableBase (clase base de IOLoop, AsyncHTTPClient y Resolver) | aplicada | 0.846 | 1419 / 4 / 1 | **ROMPE TESTS** |
| 06_rename_parametro | Rename | parámetro plus de escape.url_escape -> use_plus (los llamadores lo pasan por nombre) | aplicada | 0.594 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |
| 07_extract_boundary | Extract Method | quitar comillas del boundary en parse_multipart_form_data -> _unquote_boundary | aplicada | 0.159 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |
| 08_extract_rango | Extract Method | separar unidad y valor en _parse_request_range -> _split_range_header (2 valores de salida) | aplicada | 0.027 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |
| 09_extract_con_return | Extract Method | try/except con `return None` de _parse_request_range -> _parse_range_bounds (caso límite) | error: RefactoringError: Return should be the last statement. | 0.006 | — | **RECHAZADA POR ROPE** |
| 10_extract_bucle | Extract Method | bucle que copia argumentos urlencoded en parse_body_arguments -> _merge_urlencoded_arguments | aplicada | 0.029 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |
| 11_inline_funcion | Inline | inline de httputil._int_or_none en _parse_request_range (2 llamadas; reasigna su parámetro y tiene 2 return) | aplicada | 0.434 | 1401 / 23 / 0 | **ROMPE TESTS** |
| 12_move_funcion | Move | mover tcpclient._format_addr a netutil (los tests la importan) | aplicada | 0.894 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |
| 13_rename_parcheada | Rename | BaseIOStream._try_inline_read -> _read_inline_if_possible (los tests la parchean con mock.patch("tornado.iostream.BaseIOStream._try_inline_read")) | aplicada | 0.698 | 1421 / 0 / 3 | **ROMPE TESTS** |
| 14_rename_con_doctest | Rename | httputil._normalize_header -> _to_header_case (tiene un doctest en su docstring) | aplicada | 0.506 | 1423 / 1 / 0 | **ROMPE TESTS** |
| 15_rename_con_doctest_docs | Rename | igual que 14 pero con docs=True | aplicada | 0.513 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |
| 16_rename_en_test_modules | Rename | httputil.doctests -> doctest_suite (runtests.TEST_MODULES la nombra como string) | aplicada | 0.622 | 1411 / 0 / 1 | **ROMPE TESTS** |
| 17_rename_verbo_http | Rename | método get de HelloHandler -> handle_get (Tornado despacha con getattr(self, método_http)) | aplicada | 1.555 | 1423 / 1 / 0 | **ROMPE TESTS** |
| 18_rename_handler_string | Rename | clase HelloHandler -> GreetingHandler (las rutas la nombran como string "tornado.test.web_test.HelloHandler") | aplicada | 0.767 | 1423 / 0 / 1 | **ROMPE TESTS** |
| 19_rename_modulo | Rename (módulo) | módulo tornado/locks.py -> tornado/sync.py (tornado.__all__ lo nombra como string) | aplicada | 1.416 | 1423 / 1 / 0 | **ROMPE TESTS** |
| 20_extract_await | Extract Method | bloque con `await` de RequestHandler._execute (async def) -> _run_prepare | aplicada | 0.57 | 0 / 0 / 1 | **ROMPE TESTS** |

## Huella de carbono (CodeCarbon)

| Experimento | Fase | Duración (s) | Energía (Wh) | Emisiones (mg CO2eq) | Muestras (0,1 s) | Energía de la traza (Wh) | Pico (W) |
|---|---|---|---|---|---|---|---|
| 00_reposo | reposo | 20.006 | 0.0279 | 7.240 | 191 | 0.0277 | 5.4 |
| 00_linea_base | tests (media de 3) | 18.404 | 0.0265 | 6.869 | 176 | 0.0259 | 9.5 |
| 01_analisis | analisis | 2.274 | 0.0035 | 0.914 | 20 | 0.0034 | 7.8 |
| 02_rename_funcion | rope (media de 5) | 1.061 | 0.0017 | 0.445 | 4 | 0.0016 | 6.6 |
| 02_rename_funcion | tests | 18.930 | 0.0265 | 6.874 | 182 | 0.0263 | 5.3 |
| 03_rename_funcion_importada | rope (media de 5) | 0.791 | 0.0011 | 0.298 | 2 | 0.0011 | 5.5 |
| 03_rename_funcion_importada | tests | 18.690 | 0.0263 | 6.823 | 179 | 0.0260 | 6.4 |
| 04_rename_metodo | rope (media de 5) | 1.186 | 0.0025 | 0.653 | 3 | 0.0024 | 9.6 |
| 04_rename_metodo | tests | 18.987 | 0.0271 | 7.039 | 182 | 0.0265 | 5.7 |
| 05_rename_clase | rope (media de 5) | 0.846 | 0.0013 | 0.347 | 3 | 0.0013 | 6.1 |
| 05_rename_clase | tests | 18.855 | 0.0263 | 6.820 | 181 | 0.0263 | 7.0 |
| 06_rename_parametro | rope (media de 5) | 0.594 | 0.0009 | 0.226 | 2 | 0.0008 | 5.4 |
| 06_rename_parametro | tests | 18.877 | 0.0263 | 6.821 | 181 | 0.0262 | 5.1 |
| 07_extract_boundary | rope (media de 5) | 0.159 | 0.0002 | 0.059 | 0 | 0.0002 | 5.2 |
| 07_extract_boundary | tests | 18.629 | 0.0260 | 6.758 | 178 | 0.0259 | 5.8 |
| 08_extract_rango | rope (media de 5) | 0.027 | 0.0000 | 0.010 | 0 | 0.0000 | 0.0 |
| 08_extract_rango | tests | 18.847 | 0.0263 | 6.825 | 181 | 0.0263 | 5.6 |
| 09_extract_con_return | rope | 0.006 | 0.0000 | 0.002 | 0 | 0.0000 | 0.0 |
| 10_extract_bucle | rope (media de 5) | 0.029 | 0.0000 | 0.012 | 0 | 0.0000 | 0.0 |
| 10_extract_bucle | tests | 18.800 | 0.0263 | 6.822 | 180 | 0.0261 | 5.3 |
| 11_inline_funcion | rope (media de 5) | 0.434 | 0.0006 | 0.160 | 1 | 0.0005 | 5.4 |
| 11_inline_funcion | tests | 18.979 | 0.0265 | 6.873 | 182 | 0.0264 | 5.9 |
| 12_move_funcion | rope (media de 5) | 0.894 | 0.0013 | 0.338 | 3 | 0.0012 | 8.3 |
| 12_move_funcion | tests | 18.825 | 0.0262 | 6.807 | 180 | 0.0261 | 5.4 |
| 13_rename_parcheada | rope (media de 5) | 0.698 | 0.0010 | 0.265 | 2 | 0.0009 | 5.4 |
| 13_rename_parcheada | tests | 18.914 | 0.0263 | 6.837 | 181 | 0.0262 | 5.7 |
| 14_rename_con_doctest | rope (media de 5) | 0.506 | 0.0007 | 0.191 | 1 | 0.0006 | 5.5 |
| 14_rename_con_doctest | tests | 19.016 | 0.0265 | 6.890 | 178 | 0.0264 | 5.6 |
| 15_rename_con_doctest_docs | rope (media de 5) | 0.513 | 0.0009 | 0.230 | 1 | 0.0007 | 5.2 |
| 15_rename_con_doctest_docs | tests | 19.095 | 0.0266 | 6.903 | 176 | 0.0265 | 5.7 |
| 16_rename_en_test_modules | rope (media de 5) | 0.622 | 0.0009 | 0.229 | 1 | 0.0008 | 5.2 |
| 16_rename_en_test_modules | tests | 19.149 | 0.0267 | 6.922 | 177 | 0.0266 | 5.6 |
| 17_rename_verbo_http | rope (media de 5) | 1.555 | 0.0022 | 0.575 | 8 | 0.0022 | 5.4 |
| 17_rename_verbo_http | tests | 19.090 | 0.0266 | 6.907 | 177 | 0.0266 | 5.3 |
| 18_rename_handler_string | rope (media de 5) | 0.767 | 0.0011 | 0.281 | 2 | 0.0010 | 5.2 |
| 18_rename_handler_string | tests | 19.138 | 0.0267 | 6.930 | 178 | 0.0266 | 5.2 |
| 19_rename_modulo | rope (media de 5) | 1.416 | 0.0020 | 0.524 | 4 | 0.0020 | 5.3 |
| 19_rename_modulo | tests | 19.096 | 0.0266 | 6.898 | 177 | 0.0265 | 5.8 |
| 20_extract_await | rope (media de 5) | 0.570 | 0.0008 | 0.210 | 2 | 0.0008 | 5.3 |
| 20_extract_await | tests | 0.210 | 0.0003 | 0.076 | 1 | 0.0002 | 5.0 |

### Totales

| Concepto | Duración (s) | Energía (Wh) | Emisiones (mg CO2eq) |
|---|---|---|---|
| Todas las operaciones de Rope (91) | 63.35 | 0.0974 | 25.272 |
| Análisis estático | 2.27 | 0.0035 | 0.914 |
| Todas las corridas de tests | 377.34 | 0.5296 | 137.432 |
| **Experimento completo** (sin reposo) | 442.96 | 0.6305 | 163.617 |

- Reposo (20 s sin carga): potencia media 5.02 W.
- Factor de emisión usado: 259.5 g CO2eq/kWh.
- Sensibilidad: con el TDP genérico de 85 W que CodeCarbon usa por defecto en este equipo, el experimento completo habría reportado 1.4799 Wh y 384.048 mg CO2eq.
- Una operación de Rope: media 0.696 s, 0.0011 Wh, 0.278 mg CO2eq (desv. 0.230 mg).
- Una corrida de la suite (línea base): media 18.40 s, 0.0265 Wh, 6.869 mg CO2eq (desv. 0.254 mg).
- Medición continua: cada fase se muestreó cada 0,1 s (`traza_carbono.csv`, 3993 muestras en total). Energía integrada de la traza en todo el experimento: 0.6186 Wh frente a 0.6305 Wh de CodeCarbon (que solo calcula el total al terminar cada fase).
