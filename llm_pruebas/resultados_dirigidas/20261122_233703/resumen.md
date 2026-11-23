# Pruebas dirigidas con un LLM (tornado)

- Python: `3.12.15`
- SDK anthropic: `2.8.0`
- Modelo solicitado: `claude-sonnet-5-5` (effort `high`)
- Prompt: `prompt_v2.md` (SHA-256 `f93b3aaeb105f4b642975556690ddef7679ae083a005f9f2b3d5dd91fefdc579`)
- Fecha: 2026-11-22 23:42
- Costo total: US$ 0.4630

## Línea base

1424 passed, 0 failed, 111 skipped, 0 errors

## Corridas

| Corrida | Operación | Veredicto | Pasan/Fallan | Archivos | +/− | Residuos (código/texto) | Avisó riesgo | Costo | Tiempo (s) |
|---|---|---|---|---|---|---|---|---|---|
| 07_extract_boundary_run1 | Extract Method | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +12/−7 | - | no | 0.0412 | 11.0 |
| 07_extract_boundary_run2 | Extract Method | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +12/−7 | - | no | 0.0413 | 10.9 |
| 07_extract_boundary_run3 | Extract Method | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +7/−2 | - | no | 0.0391 | 5.4 |
| 08_extract_rango_run1 | Extract Method | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +8/−2 | - | no | 0.038 | 4.2 |
| 08_extract_rango_run2 | Extract Method | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +7/−0 | - | no | 0.0382 | 4.7 |
| 08_extract_rango_run3 | Extract Method | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +8/−2 | - | no | 0.0375 | 4.6 |
| 09_extract_con_return_run1 | Extract Method | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +14/−4 | - | no | 0.0387 | 5.0 |
| 09_extract_con_return_run2 | Extract Method | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +14/−4 | - | no | 0.0381 | 4.7 |
| 09_extract_con_return_run3 | Extract Method | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +14/−4 | - | no | 0.038 | 5.1 |
| 10_extract_bucle_run1 | Extract Method | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +9/−3 | - | no | 0.038 | 4.3 |
| 10_extract_bucle_run2 | Extract Method | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +10/−3 | - | no | 0.0374 | 4.4 |
| 10_extract_bucle_run3 | Extract Method | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +10/−3 | - | no | 0.0375 | 4.5 |

## Por caso

| Caso | Corridas | Preservan | Solo formato | Rompen | Inválidas | Otras |
|---|---|---|---|---|---|---|
| 07_extract_boundary | 3 | 3 | 0 | 0 | 0 | 0 |
| 08_extract_rango | 3 | 3 | 0 | 0 | 0 | 0 |
| 09_extract_con_return | 3 | 3 | 0 | 0 | 0 | 0 |
| 10_extract_bucle | 3 | 3 | 0 | 0 | 0 | 0 |
