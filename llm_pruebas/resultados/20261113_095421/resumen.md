# Resumen de pruebas con LLM (prompt general) — Tornado

- Python: `3.12.15`
- SDK anthropic: `2.8.0`
- Modelo solicitado: `claude-sonnet-5-5` (effort `high`)
- Prompt: `prompt_v1.md`
- Corridas por módulo: 3
- Fecha: 2026-11-13 11:59
- Costo total estimado: US$ 9.07

## Línea base

1535 tests: 1424 passed, 0 failed, 111 skipped, 0 errors

## Corridas

| Corrida | Modelo | +/− líneas | Tests (passed/failed/errors) | Veredicto | Tipo de fallo | Cambios API pública | Tiempo (s) | Costo (US$) |
|---|---|---|---|---|---|---|---|---|
| escape_run1 | claude-sonnet-5-5 | +58 / −42 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | — | 43.2 | 0.9039 |
| escape_run2 | claude-sonnet-5-5 | +58 / −47 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | — | 42.2 | 0.1104 |
| escape_run3 | claude-sonnet-5-5 | +66 / −48 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | — | 46.3 | 0.115 |
| netutil_run1 | claude-sonnet-5-5 | +130 / −97 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | — | 81.3 | 0.1637 |
| netutil_run2 | claude-sonnet-5-5 | +121 / −82 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | — | 81.9 | 0.9601 |
| netutil_run3 | claude-sonnet-5-5 | +136 / −90 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | — | 82.1 | 0.1737 |
| locks_run1 | claude-sonnet-5-5 | +45 / −36 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | eliminado import Optional; eliminado import Type | 53.3 | 0.1171 |
| locks_run2 | claude-sonnet-5-5 | +50 / −40 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | eliminado import Optional; eliminado import Type | 54.2 | 0.1221 |
| locks_run3 | claude-sonnet-5-5 | +45 / −34 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | — | 49.7 | 0.1177 |
| tcpclient_run1 | claude-sonnet-5-5 | +95 / −64 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | eliminado import Tuple | 46.5 | 0.1151 |
| tcpclient_run2 | claude-sonnet-5-5 | +97 / −56 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | eliminado import Tuple | 44.8 | 0.1136 |
| tcpclient_run3 | claude-sonnet-5-5 | +130 / −72 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | eliminado import Tuple | 50.7 | 0.1234 |
| util_run1 | claude-sonnet-5-5 | +45 / −21 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | — | 54.2 | 0.1359 |
| util_run2 | claude-sonnet-5-5 | +58 / −33 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | — | 55.0 | 0.1376 |
| util_run3 | claude-sonnet-5-5 | +52 / −29 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | — | 54.5 | 0.1357 |
| httputil_run1 | claude-sonnet-5-5 | +191 / −154 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | — | 159.6 | 0.2953 |
| httputil_run2 | claude-sonnet-5-5 | +184 / −137 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | — | 136.2 | 0.2764 |
| httputil_run3 | claude-sonnet-5-5 | +193 / −142 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | — | 133.7 | 0.2741 |
| iostream_run1 | claude-sonnet-5-5 | +240 / −177 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | — | 168.4 | 0.3532 |
| iostream_run2 | claude-sonnet-5-5 | +283 / −218 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | — | 149.5 | 0.3256 |
| iostream_run3 | claude-sonnet-5-5 | +219 / −163 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | — | 147.2 | 0.3221 |
| web_run1 | claude-sonnet-5-5 | +275 / −189 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | — | 318.5 | 0.6847 |
| web_run2 | claude-sonnet-5-5 | +361 / −260 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | — | 335.8 | 1.5061 |
| web_run3 | claude-sonnet-5-5 | +339 / −253 | 1424 / 0 / 0 | **COMPORTAMIENTO PRESERVADO** |  | — | 323.7 | 1.4894 |

## Determinismo

| Módulo | Corridas | Diffs distintos |
|---|---|---|
| escape | 3 | 3 |
| httputil | 3 | 3 |
| iostream | 3 | 3 |
| locks | 3 | 3 |
| netutil | 3 | 3 |
| tcpclient | 3 | 3 |
| util | 3 | 3 |
| web | 3 | 3 |

## Huella de carbono local (CodeCarbon + traza continua de 0,1 s)

Solo el consumo **de este equipo**. La llamada al LLM mide al Mac esperando la respuesta por red; la energía de los servidores de Anthropic no se puede medir desde aquí (por eso se registran los tokens).

| Corrida | LLM: duración (s) | LLM: energía (Wh) | LLM: pico (W) | Tests: duración (s) | Tests: energía (Wh) | Tests: pico (W) | Emisiones locales (mg CO2eq) | Tokens salida |
|---|---|---|---|---|---|---|---|---|
| escape_run1 | 43.2 | 0.0606 | 7.4 | 19.2 | 0.0268 | 5.9 | 22.703 | 7747 |
| escape_run2 | 42.2 | 0.0585 | 5.1 | 18.8 | 0.0261 | 6.0 | 21.965 | 7731 |
| escape_run3 | 46.3 | 0.0643 | 5.1 | 18.8 | 0.0261 | 6.2 | 23.458 | 8194 |
| netutil_run1 | 81.3 | 0.1130 | 6.4 | 18.8 | 0.0261 | 6.4 | 36.104 | 13060 |
| netutil_run2 | 755.8 | 1.0642 | 14.6 | 21.9 | 0.0315 | 11.7 | 284.355 | 13374 |
| netutil_run3 | 82.1 | 0.1160 | 12.9 | 18.8 | 0.0266 | 8.3 | 37.003 | 14061 |
| locks_run1 | 53.3 | 0.0750 | 10.5 | 19.0 | 0.0267 | 6.7 | 26.380 | 8401 |
| locks_run2 | 54.2 | 0.0756 | 5.4 | 19.1 | 0.0267 | 6.4 | 26.540 | 8897 |
| locks_run3 | 49.7 | 0.0705 | 11.9 | 19.1 | 0.0267 | 6.0 | 25.234 | 8464 |
| tcpclient_run1 | 46.5 | 0.0653 | 23.0 | 19.1 | 0.0267 | 6.5 | 23.895 | 8200 |
| tcpclient_run2 | 44.8 | 0.0633 | 23.0 | 18.9 | 0.0280 | 12.3 | 23.690 | 8050 |
| tcpclient_run3 | 50.7 | 0.0706 | 5.5 | 18.9 | 0.0263 | 5.5 | 25.143 | 9031 |
| util_run1 | 54.2 | 0.0757 | 7.8 | 18.5 | 0.0258 | 7.2 | 26.358 | 10275 |
| util_run2 | 55.0 | 0.0768 | 7.4 | 18.8 | 0.0261 | 5.3 | 26.704 | 10451 |
| util_run3 | 54.5 | 0.0760 | 6.6 | 18.7 | 0.0264 | 8.9 | 26.586 | 10255 |
| httputil_run1 | 159.6 | 0.2216 | 5.4 | 19.0 | 0.0269 | 23.0 | 64.506 | 26223 |
| httputil_run2 | 136.2 | 0.1892 | 7.2 | 19.1 | 0.0264 | 5.1 | 55.944 | 24328 |
| httputil_run3 | 133.7 | 0.1856 | 5.2 | 19.0 | 0.0263 | 5.2 | 54.997 | 24098 |
| iostream_run1 | 168.4 | 0.2339 | 5.3 | 19.1 | 0.0265 | 5.3 | 67.574 | 32013 |
| iostream_run2 | 149.5 | 0.2076 | 5.1 | 19.0 | 0.0265 | 5.1 | 60.732 | 29247 |
| iostream_run3 | 147.2 | 0.2055 | 23.0 | 18.9 | 0.0262 | 5.4 | 60.124 | 28897 |
| web_run1 | 318.5 | 0.4449 | 23.0 | 19.1 | 0.0265 | 5.1 | 122.319 | 65155 |
| web_run2 | 335.8 | 0.4670 | 7.7 | 19.0 | 0.0264 | 5.1 | 128.028 | 67973 |
| web_run3 | 323.7 | 0.4506 | 23.0 | 19.1 | 0.0264 | 5.3 | 123.787 | 66304 |

### Totales

| Fase | n | Duración (s) | Energía traza (Wh) | Energía CodeCarbon (Wh) | Emisiones (mg CO2eq) |
|---|---|---|---|---|---|
| Llamadas al LLM (espera local) | 24 | 3386.5 | 4.7314 | 4.7878 | 1227.852 |
| Corridas de tests | 24 | 457.4 | 0.6407 | 0.6513 | 166.278 |

- Reposo (20 s sin carga): potencia media 5.00 W.
- CodeCarbon 3.3.2, país `COL`, CPU `Apple M4` TDP 20.0 W.

Las refactorizaciones que el modelo dice haber aplicado están al final de cada `<corrida>_respuesta.md`.
