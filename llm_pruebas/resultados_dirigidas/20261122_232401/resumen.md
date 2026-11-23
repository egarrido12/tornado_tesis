# Pruebas dirigidas con un LLM (tornado)

- Python: `3.12.15`
- SDK anthropic: `2.8.0`
- Modelo solicitado: `claude-sonnet-5-5` (effort `high`)
- Prompt: `prompt_v2.md` (SHA-256 `f93b3aaeb105f4b642975556690ddef7679ae083a005f9f2b3d5dd91fefdc579`)
- Fecha: 2026-11-22 23:37
- Costo total: US$ 1.9066

## Línea base

1424 passed, 0 failed, 111 skipped, 0 errors

## Corridas

| Corrida | Operación | Veredicto | Pasan/Fallan | Archivos | +/− | Residuos (código/texto) | Avisó riesgo | Costo | Tiempo (s) |
|---|---|---|---|---|---|---|---|---|---|
| 02_rename_funcion_run1 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 6 | +28/−24 | 0/0 | sí | 0.2236 | 37.1 |
| 02_rename_funcion_run2 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 6 | +26/−24 | 0/0 | sí | 0.0833 | 28.5 |
| 02_rename_funcion_run3 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 6 | +28/−24 | 0/0 | sí | 0.0838 | 27.9 |
| 03_rename_funcion_importada_run1 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 6 | +21/−21 | 0/0 | sí | 0.1575 | 16.0 |
| 03_rename_funcion_importada_run2 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 6 | +21/−21 | 0/0 | sí | 0.0593 | 13.3 |
| 03_rename_funcion_importada_run3 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 6 | +21/−21 | 0/0 | sí | 0.0603 | 13.5 |
| 04_rename_metodo_run1 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 2 | +5/−5 | 0/0 | sí | 0.1046 | 13.6 |
| 04_rename_metodo_run2 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 2 | +5/−5 | 0/0 | sí | 0.0493 | 10.1 |
| 04_rename_metodo_run3 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +4/−4 | 1/0 | sí | 0.0431 | 7.7 |
| 05_rename_clase_run1 | Rename | **EDICIÓN INVÁLIDA** | -/- | 0 | +-/−- | - | sí | 0.2188 | 45.1 |
| 05_rename_clase_run2 | Rename | **EDICIÓN INVÁLIDA** | -/- | 0 | +-/−- | - | sí | 0.1224 | 46.4 |
| 05_rename_clase_run3 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 7 | +51/−47 | 7/0 | sí | 0.1256 | 49.8 |
| 06_rename_parametro_run1 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 5 | +18/−16 | - | sí | 0.176 | 16.1 |
| 06_rename_parametro_run2 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 5 | +15/−13 | - | sí | 0.06 | 15.3 |
| 06_rename_parametro_run3 | Rename | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 5 | +15/−13 | - | sí | 0.0627 | 16.6 |
| 11_inline_funcion_run1 | Inline | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +2/−8 | - | sí | 0.039 | 5.4 |
| 11_inline_funcion_run2 | Inline | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +4/−8 | - | sí | 0.0391 | 5.8 |
| 11_inline_funcion_run3 | Inline | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 1 | +2/−9 | - | sí | 0.0388 | 5.6 |
| 12_move_funcion_run1 | Move | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 3 | +17/−17 | - | sí | 0.0687 | 9.3 |
| 12_move_funcion_run2 | Move | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 3 | +17/−17 | - | sí | 0.0467 | 9.3 |
| 12_move_funcion_run3 | Move | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 3 | +17/−17 | - | sí | 0.044 | 7.4 |

## Por caso

| Caso | Corridas | Preservan | Solo formato | Rompen | Inválidas | Otras |
|---|---|---|---|---|---|---|
| 02_rename_funcion | 3 | 3 | 0 | 0 | 0 | 0 |
| 03_rename_funcion_importada | 3 | 3 | 0 | 0 | 0 | 0 |
| 04_rename_metodo | 3 | 3 | 0 | 0 | 0 | 0 |
| 05_rename_clase | 3 | 1 | 0 | 0 | 2 | 0 |
| 06_rename_parametro | 3 | 3 | 0 | 0 | 0 | 0 |
| 11_inline_funcion | 3 | 3 | 0 | 0 | 0 | 0 |
| 12_move_funcion | 3 | 3 | 0 | 0 | 0 | 0 |
