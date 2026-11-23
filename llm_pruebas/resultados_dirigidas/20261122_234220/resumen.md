# Pruebas dirigidas con un LLM (tornado)

- Python: `3.12.15`
- SDK anthropic: `2.8.0`
- Modelo solicitado: `claude-sonnet-5-5` (effort `high`)
- Prompt: `prompt_v2.md` (SHA-256 `f93b3aaeb105f4b642975556690ddef7679ae083a005f9f2b3d5dd91fefdc579`)
- Fecha: 2026-11-22 23:56
- Costo total: US$ 2.5417

## Línea base

1424 passed, 0 failed, 111 skipped, 0 errors

## Corridas

| Corrida | Operación | Veredicto | Pasan/Fallan | Archivos | +/− | Residuos (código/texto) | Avisó riesgo | Costo | Tiempo (s) |
|---|---|---|---|---|---|---|---|---|---|
| 13_rename_parcheada_run1 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 2 | +7/−7 | 1/0 | sí | 0.1101 | 17.5 |
| 13_rename_parcheada_run2 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 2 | +7/−7 | 1/0 | sí | 0.0538 | 13.6 |
| 13_rename_parcheada_run3 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 2 | +7/−7 | 1/0 | no | 0.0524 | 14.3 |
| 14_rename_con_doctest_run1 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +8/−8 | 0/0 | sí | 0.0437 | 7.9 |
| 14_rename_con_doctest_run2 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +8/−8 | 0/0 | sí | 0.0434 | 7.8 |
| 14_rename_con_doctest_run3 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +8/−8 | 0/0 | sí | 0.0445 | 8.7 |
| 15_rename_con_doctest_docs_run1 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +8/−8 | 0/0 | sí | 0.0493 | 12.5 |
| 15_rename_con_doctest_docs_run2 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +8/−8 | 0/0 | sí | 0.0486 | 12.0 |
| 15_rename_con_doctest_docs_run3 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +8/−8 | 0/0 | sí | 0.0486 | 12.5 |
| 16_rename_en_test_modules_run1 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 3 | +3/−3 | 2/0 | sí | 0.1432 | 9.0 |
| 16_rename_en_test_modules_run2 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 3 | +3/−3 | 2/0 | sí | 0.0452 | 8.6 |
| 16_rename_en_test_modules_run3 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 3 | +3/−3 | 2/0 | sí | 0.046 | 9.1 |
| 17_rename_verbo_http_run1 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +4/−1 | - | sí | 0.3258 | 9.7 |
| 17_rename_verbo_http_run2 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +3/−1 | - | sí | 0.0526 | 8.7 |
| 17_rename_verbo_http_run3 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +3/−1 | - | sí | 0.0516 | 15.2 |
| 18_rename_handler_string_run1 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +4/−4 | 4/0 | sí | 0.3277 | 8.2 |
| 18_rename_handler_string_run2 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +4/−4 | 4/0 | sí | 0.0537 | 10.4 |
| 18_rename_handler_string_run3 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +4/−4 | 4/0 | sí | 0.0528 | 7.5 |
| 19_rename_modulo_run1 | Rename (módulo) | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 13 | +48/−47 | 5/0 | sí | 0.6224 | 36.2 |
| 19_rename_modulo_run2 | Rename (módulo) | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 14 | +53/−52 | 1/0 | sí | 0.1075 | 35.0 |
| 19_rename_modulo_run3 | Rename (módulo) | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 13 | +47/−46 | 5/0 | sí | 0.0956 | 27.0 |
| 20_extract_await_run1 | Extract Method | **ROMPE TESTS** | 320/869 | 1 | +1/−3 | - | sí | 0.041 | 7.5 |
| 20_extract_await_run2 | Extract Method | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +6/−3 | - | sí | 0.0417 | 7.8 |
| 20_extract_await_run3 | Extract Method | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +7/−3 | - | sí | 0.0405 | 6.9 |

## Por caso

| Caso | Corridas | Preservan | Solo formato | Rompen | Inválidas | Otras |
|---|---|---|---|---|---|---|
| 13_rename_parcheada | 3 | 3 | 0 | 0 | 0 | 0 |
| 14_rename_con_doctest | 3 | 3 | 0 | 0 | 0 | 0 |
| 15_rename_con_doctest_docs | 3 | 3 | 0 | 0 | 0 | 0 |
| 16_rename_en_test_modules | 3 | 3 | 0 | 0 | 0 | 0 |
| 17_rename_verbo_http | 3 | 3 | 0 | 0 | 0 | 0 |
| 18_rename_handler_string | 3 | 3 | 0 | 0 | 0 | 0 |
| 19_rename_modulo | 3 | 3 | 0 | 0 | 0 | 0 |
| 20_extract_await | 3 | 2 | 0 | 1 | 0 | 0 |
