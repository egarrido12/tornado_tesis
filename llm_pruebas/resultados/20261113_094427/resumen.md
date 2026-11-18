# Resumen de pruebas con LLM (prompt general) — Tornado

- Python: `3.12.15`
- SDK anthropic: `2.8.0`
- Modelo solicitado: `claude-sonnet-5-5` (effort `high`)
- Prompt: `prompt_v1.md`
- Corridas por módulo: 1
- Fecha: 2026-11-13 09:46
- Costo total estimado: US$ 0.91

## Línea base

1535 tests: 1424 passed, 0 failed, 111 skipped, 0 errors

## Corridas

| Corrida | Modelo | +/− líneas | Tests (passed/failed/errors) | Veredicto | Tipo de fallo | Cambios API pública | Tiempo (s) | Costo (US$) |
|---|---|---|---|---|---|---|---|---|
| escape_run1 | claude-sonnet-5-5 | +62 / −46 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | — | 47.3 | 0.9098 |

## Determinismo

| Módulo | Corridas | Diffs distintos |
|---|---|---|
| escape | 1 | 1 |

## Huella de carbono local (CodeCarbon + traza continua de 0,1 s)

Solo el consumo **de este equipo**. La llamada al LLM mide al Mac esperando la respuesta por red; la energía de los servidores de Anthropic no se puede medir desde aquí (por eso se registran los tokens).

| Corrida | LLM: duración (s) | LLM: energía (Wh) | LLM: pico (W) | Tests: duración (s) | Tests: energía (Wh) | Tests: pico (W) | Emisiones locales (mg CO2eq) | Tokens salida |
|---|---|---|---|---|---|---|---|---|
| escape_run1 | 47.3 | 0.0657 | 6.4 | 19.0 | 0.0265 | 5.6 | 23.930 | 8343 |

### Totales

| Fase | n | Duración (s) | Energía traza (Wh) | Energía CodeCarbon (Wh) | Emisiones (mg CO2eq) |
|---|---|---|---|---|---|
| Llamadas al LLM (espera local) | 1 | 47.3 | 0.0657 | 0.0659 | 17.059 |
| Corridas de tests | 1 | 19.0 | 0.0265 | 0.0266 | 6.871 |

- Reposo (20 s sin carga): potencia media 5.01 W.
- CodeCarbon 3.3.2, país `COL`, CPU `Apple M4` TDP 20.0 W.

Las refactorizaciones que el modelo dice haber aplicado están al final de cada `<corrida>_respuesta.md`.
