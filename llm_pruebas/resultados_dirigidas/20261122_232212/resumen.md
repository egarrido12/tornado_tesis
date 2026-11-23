# Pruebas dirigidas con un LLM (tornado)

- Python: `3.12.15`
- SDK anthropic: `2.8.0`
- Modelo solicitado: `claude-sonnet-5-5` (effort `high`)
- Prompt: `prompt_v2.md` (SHA-256 `f93b3aaeb105f4b642975556690ddef7679ae083a005f9f2b3d5dd91fefdc579`)
- Fecha: 2026-11-22 23:23
- Costo total: US$ 1.4048

## Línea base

1424 passed, 0 failed, 111 skipped, 0 errors

## Corridas

| Corrida | Operación | Veredicto | Pasan/Fallan | Archivos | +/− | Residuos (código/texto) | Avisó riesgo | Costo | Tiempo (s) |
|---|---|---|---|---|---|---|---|---|---|
| 12_move_funcion_run1 | Move | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 3 | +17/−17 | - | sí | 1.3592 | 14.0 |
| 12_move_funcion_run2 | Move | **COMPORTAMIENTO PRESERVADO** | 1424/0 | 3 | +17/−17 | - | sí | 0.0456 | 10.7 |

## Por caso

| Caso | Corridas | Preservan | Solo formato | Rompen | Inválidas | Otras |
|---|---|---|---|---|---|---|
| 12_move_funcion | 2 | 2 | 0 | 0 | 0 | 0 |
