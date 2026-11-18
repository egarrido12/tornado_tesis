"""Pruebas de Tornado con un LLM (refactorización con un prompt general) + carbono.

Réplica del experimento hecho sobre PySnooper y Cookiecutter
(../../cookiecutter_tesis/llm_pruebas). A diferencia de rope_pruebas/, aquí NO
se le indica al modelo qué refactorización hacer: recibe un prompt general
(prompt_v1.md) y decide él mismo qué cambiar en cada módulo.

Flujo:
  0. Reposo: mide el consumo del equipo sin hacer nada (ruido de fondo).
  1. Línea base: corre la suite original de Tornado.
  2. Para cada módulo y cada corrida: se envía el prompt + el paquete completo
     como contexto, se extrae el archivo refactorizado, se aplica sobre una
     copia limpia, se guarda el diff, se compara la API pública (con ast) y se
     corre la suite de tests.
  3. Se escribe un resumen (tests, API, tokens, costo, determinismo, carbono).

Carbono (novedad respecto de las otras pruebas con LLM): cada llamada a la API y
cada corrida de tests se miden con CodeCarbon MÁS un muestreo de potencia cada
0,1 s DURANTE la ejecución (ver rope_pruebas/carbono_traza.py). Se guarda la
curva completa en traza_carbono.csv. De la llamada al LLM solo se mide el consumo
LOCAL (el equipo esperando por red); la energía de los servidores de Anthropic no
es medible desde aquí, por eso se registran también los tokens.

Por defecto usa Claude Sonnet 5.5 (más barato que Opus 5.5, el modelo de las
pruebas de Cookiecutter) para ajustarse al presupuesto de tokens.

El código original en ../tornado NUNCA se modifica. Cada ejecución se guarda en
resultados/<fecha_hora>/ para no sobrescribir corridas pagadas.

Uso (desde la raíz del repositorio, con ANTHROPIC_API_KEY exportada):
    .venv/bin/python llm_pruebas/ejecutar_pruebas_llm.py --dry-run
    .venv/bin/python llm_pruebas/ejecutar_pruebas_llm.py --modulos escape --corridas 1
    .venv/bin/python llm_pruebas/ejecutar_pruebas_llm.py
"""
import argparse
import ast
import difflib
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path

import anthropic

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parent
sys.path.insert(0, str(REPO / 'rope_pruebas'))
from carbono_traza import Medidor  # noqa: E402

PAQUETE = REPO / 'tornado'
TRABAJO = AQUI / '_trabajo'
RESULTADOS = AQUI / 'resultados'
PYTHON = sys.executable
PROMPT = AQUI / 'prompt_v1.md'

MODULOS = sorted(p.stem for p in PAQUETE.glob('*.py'))
# Módulos que tocan las pruebas de Rope (02-20): son los que se pueden comparar.
MODULOS_POR_DEFECTO = ['escape', 'netutil', 'locks', 'tcpclient', 'util',
                       'httputil', 'iostream', 'web']

PAIS = os.environ.get('CODECARBON_PAIS', 'COL')
TDP_CPU_W = float(os.environ.get('CODECARBON_TDP', '20'))   # ver rope_pruebas
SEGUNDOS_REPOSO = 20

IGNORAR = shutil.ignore_patterns(
    '.git', '.github', '.venv', '*.egg-info', '__pycache__', '.ropeproject',
    '.mypy_cache', '.tox', 'build', 'rope_pruebas', 'llm_pruebas', 'docs',
    'demos', 'maint',
)

# USD por millón de tokens: (input, output, escritura de caché, lectura de caché)
PRECIOS = {
    'claude-opus-5-5': (4.00, 20.00, 5.00, 0.20),
    'claude-sonnet-5-5': (2.00, 10.00, 2.50, 0.10),
    'claude-fable-5-2': (8.00, 40.00, 10.00, 0.20),
}

MEDICIONES = []


# ---------------------------------------------------------------------------
# Utilidades (tests, copias, API pública)
# ---------------------------------------------------------------------------

def copia_limpia(nombre):
    destino = TRABAJO / nombre
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(REPO, destino, ignore=IGNORAR)
    return destino


def correr_tests(carpeta):
    """Suite oficial de Tornado (unittest). Misma función que en rope_pruebas."""
    env = dict(os.environ, PYTHONPATH=str(carpeta))
    proc = subprocess.run([PYTHON, '-m', 'tornado.test.runtests'],
                          cwd=carpeta, capture_output=True, text=True, env=env)
    salida = proc.stdout + proc.stderr
    resumen = {'returncode': proc.returncode}
    m = re.search(r'^Ran (\d+) tests? in', salida, re.M)
    ejecutados = int(m.group(1)) if m else 0
    for clave, patron in (('failed', 'failures'), ('errors', 'errors'),
                          ('skipped', 'skipped'),
                          ('expected_failures', 'expected failures')):
        m2 = re.search(r'^(?:OK|FAILED) \(.*\b' + patron + r'=(\d+)', salida, re.M)
        resumen[clave] = int(m2.group(1)) if m2 else 0
    if not m:
        resumen['errors'] = max(resumen['errors'], 1)
    resumen['ran'] = ejecutados
    resumen['passed'] = max(ejecutados - resumen['failed'] - resumen['errors']
                            - resumen['skipped'] - resumen['expected_failures'], 0)
    return resumen, salida


def verificar_sin_tornado_instalado():
    import importlib.metadata
    try:
        importlib.metadata.distribution('tornado')
    except importlib.metadata.PackageNotFoundError:
        return
    sys.exit('tornado está instalado en %s; desinstálalo para que los tests '
             'usen solo la copia.' % sys.prefix)


def contexto_paquete():
    """Todos los módulos de tornado/ (nivel superior) como bloques <archivo>."""
    partes = []
    for ruta in sorted(PAQUETE.glob('*.py')):
        rel = ruta.relative_to(REPO).as_posix()
        partes.append('<archivo ruta="%s">\n%s\n</archivo>' % (rel, ruta.read_text()))
    return 'Código actual del paquete tornado:\n\n' + '\n\n'.join(partes)


def extraer_codigo(texto):
    """Devuelve el bloque ```python más largo de la respuesta (o None)."""
    bloques = re.findall(r'```(?:python|py)?[ \t]*\n(.*?)```', texto, re.DOTALL)
    return max(bloques, key=len) if bloques else None


def costo(modelo, uso):
    precios = PRECIOS.get(modelo)
    if not precios:
        return None
    p_in, p_out, p_cw, p_cr = precios
    return round((uso['input'] * p_in + uso['output'] * p_out
                  + uso['cache_write'] * p_cw + uso['cache_read'] * p_cr) / 1e6, 4)


def clasificar_fallo(codigo, salida_tests):
    try:
        compile(codigo, '<llm>', 'exec')
    except SyntaxError as e:
        return 'sintaxis: %s' % e
    if re.search(r'ImportError|cannot import name|has no attribute|ModuleNotFoundError',
                 salida_tests):
        return 'API rota (import/atributo)'
    return 'comportamiento'


def api_publica(codigo):
    """Nombres públicos de nivel de módulo y firmas de funciones/métodos públicos."""
    def firma(nodo):
        a = nodo.args
        partes = [p.arg for p in a.posonlyargs] + ['/'] * bool(a.posonlyargs)
        partes += [p.arg for p in a.args]
        partes += ['*' + a.vararg.arg] if a.vararg else (['*'] if a.kwonlyargs else [])
        partes += [p.arg for p in a.kwonlyargs]
        partes += ['**' + a.kwarg.arg] if a.kwarg else []
        return '(%s)' % ', '.join(partes)

    api = {}
    for nodo in ast.parse(codigo).body:
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
            api[nodo.name] = firma(nodo)
        elif isinstance(nodo, ast.ClassDef):
            api[nodo.name] = 'clase'
            for hijo in nodo.body:
                if (isinstance(hijo, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and (not hijo.name.startswith('_') or hijo.name.startswith('__'))):
                    api['%s.%s' % (nodo.name, hijo.name)] = firma(hijo)
        elif isinstance(nodo, (ast.Assign, ast.AnnAssign)):
            objetivos = nodo.targets if isinstance(nodo, ast.Assign) else [nodo.target]
            for t in objetivos:
                if isinstance(t, ast.Name):
                    api[t.id] = 'valor'
        elif isinstance(nodo, (ast.Import, ast.ImportFrom)):
            for alias in nodo.names:
                api[(alias.asname or alias.name).split('.')[0]] = 'import'
    return {k: v for k, v in api.items() if not k.split('.')[0].startswith('_')}


def cambios_api(original, nuevo):
    try:
        antes, despues = api_publica(original), api_publica(nuevo)
    except SyntaxError:
        return ['(no se pudo analizar: error de sintaxis)']
    cambios = []
    for nombre, f in sorted(antes.items()):
        if nombre not in despues:
            cambios.append('eliminado %s %s' % (f, nombre))
        elif despues[nombre] != f:
            cambios.append('firma %s: %s -> %s' % (nombre, f, despues[nombre]))
    return cambios


# ---------------------------------------------------------------------------
# Llamada al LLM
# ---------------------------------------------------------------------------

def es_error_de_red(e):
    return (isinstance(e, (anthropic.APIConnectionError, OSError))
            or type(e).__module__.split('.')[0].startswith('httpx'))


def pedir_con_reintentos(cliente, args, sistema, contexto, modulo, intentos=4):
    for intento in range(1, intentos + 1):
        try:
            texto, meta = pedir_refactorizacion(cliente, args, sistema, contexto, modulo)
            meta['intentos'] = intento
            return texto, meta
        except Exception as e:
            if not es_error_de_red(e) or intento == intentos:
                raise
            espera = 30 * intento
            print('[%s] error de red (%s: %s), reintento %d en %ds'
                  % (modulo, type(e).__name__, e, intento, espera))
            time.sleep(espera)


def pedir_refactorizacion(cliente, args, sistema, contexto, modulo):
    """Envía el prompt general para `modulo` y devuelve (texto, metadatos)."""
    t0 = time.perf_counter()
    with cliente.beta.messages.stream(
        model=args.modelo,
        max_tokens=args.max_tokens,
        system=sistema,
        output_config={'effort': args.effort},
        # Si el modelo rechaza la petición, la API la reintenta con otro modelo;
        # queda registrado en `modelo_respuesta`.
        betas=['server-side-fallback-2026-07-01'],
        fallbacks='default',
        messages=[{'role': 'user', 'content': [
            # Prefijo idéntico en todas las llamadas -> se reutiliza la caché.
            {'type': 'text', 'text': contexto, 'cache_control': {'type': 'ephemeral'}},
            {'type': 'text', 'text': 'Refactoriza el archivo `tornado/%s.py`.' % modulo},
        ]}],
    ) as stream:
        respuesta = stream.get_final_message()
    texto = ''.join(b.text for b in respuesta.content if b.type == 'text')
    u = respuesta.usage
    uso = {
        'input': u.input_tokens,
        'output': u.output_tokens,
        'cache_write': u.cache_creation_input_tokens or 0,
        'cache_read': u.cache_read_input_tokens or 0,
    }
    meta = {
        'modelo_respuesta': respuesta.model,
        'stop_reason': respuesta.stop_reason,
        'message_id': respuesta.id,
        'tiempo_llm_s': round(time.perf_counter() - t0, 1),
        'tokens': uso,
        'costo_usd': costo(respuesta.model, uso),
    }
    return texto, meta


# ---------------------------------------------------------------------------
# Una corrida
# ---------------------------------------------------------------------------

CAMPOS_CARBONO = ('duracion_s', 'energia_kwh', 'energia_traza_kwh', 'emisiones_kg',
                  'emisiones_traza_kg', 'potencia_pico_w', 'potencia_media_traza_w',
                  'n_muestras')


def carbono_de(medicion):
    return {c: medicion[c] for c in CAMPOS_CARBONO}


def corrida(cliente, medidor, args, sistema, contexto, modulo, n, base, salida_dir):
    nombre = '%s_run%d' % (modulo, n)
    fila = {'id': nombre, 'modulo': modulo, 'corrida': n, 'carbono': {}}
    try:
        # Fase "llm": consumo local mientras se espera a la API (y se recibe el stream).
        texto, meta = medidor.medir(
            'llm', nombre,
            lambda: pedir_con_reintentos(cliente, args, sistema, contexto, modulo))
        fila['carbono']['llm'] = carbono_de(MEDICIONES[-1])
    except anthropic.APIStatusError as e:
        fila['veredicto'] = 'ERROR API %s' % e.status_code
        fila['detalle'] = str(e.message)
        print('[%s] %s' % (nombre, fila['veredicto']))
        return fila
    fila.update(meta)
    (salida_dir / (nombre + '_respuesta.md')).write_text(texto)

    if meta['stop_reason'] == 'refusal':
        fila['veredicto'] = 'RECHAZADA POR EL MODELO'
        print('[%s] %s' % (nombre, fila['veredicto']))
        return fila
    codigo = extraer_codigo(texto)
    if codigo is None:
        fila['veredicto'] = 'SIN CÓDIGO EN LA RESPUESTA'
        print('[%s] %s' % (nombre, fila['veredicto']))
        return fila

    rel = 'tornado/%s.py' % modulo
    original = (REPO / rel).read_text()
    (salida_dir / (nombre + '.py')).write_text(codigo)
    diff = ''.join(difflib.unified_diff(
        original.splitlines(True), codigo.splitlines(True), 'a/' + rel, 'b/' + rel))
    (salida_dir / (nombre + '.diff')).write_text(diff)
    fila['lineas_agregadas'] = sum(1 for l in diff.splitlines()
                                   if l.startswith('+') and not l.startswith('+++'))
    fila['lineas_eliminadas'] = sum(1 for l in diff.splitlines()
                                    if l.startswith('-') and not l.startswith('---'))
    fila['sin_cambios'] = not diff
    fila['cambios_api_publica'] = cambios_api(original, codigo)

    carpeta = copia_limpia(nombre)
    (carpeta / rel).write_text(codigo)
    resumen, salida = medidor.medir('tests', nombre, lambda: correr_tests(carpeta))
    fila['carbono']['tests'] = carbono_de(MEDICIONES[-1])
    (salida_dir / (nombre + '_tests.txt')).write_text(salida)
    fila['tests'] = resumen
    igual = (resumen['passed'] == base['passed'] and resumen['failed'] == 0
             and resumen['errors'] == 0)
    if igual:
        fila['veredicto'] = 'COMPORTAMIENTO PRESERVADO'
    else:
        fila['veredicto'] = 'ROMPE TESTS'
        fila['tipo_fallo'] = clasificar_fallo(codigo, salida)
    if meta['stop_reason'] == 'max_tokens':
        fila['veredicto'] += ' (respuesta truncada)'
    print('[%s] %s  %s  %ss  $%s  api=%s' % (
        nombre, fila['veredicto'], resumen, meta['tiempo_llm_s'], meta['costo_usd'],
        fila['cambios_api_publica'] or 'sin cambios'))
    return fila


# ---------------------------------------------------------------------------
# Reporte
# ---------------------------------------------------------------------------

def determinismo(filas, salida_dir):
    res = {}
    for modulo in sorted({f['modulo'] for f in filas}):
        diffs = [(salida_dir / (f['id'] + '.diff')).read_text()
                 for f in filas if f['modulo'] == modulo
                 and (salida_dir / (f['id'] + '.diff')).exists()]
        res[modulo] = {'corridas': len(diffs), 'diffs_distintos': len(set(diffs))}
    return res


def totales_carbono(filas, reposo):
    """Suma de la energía local por tipo de fase (CodeCarbon y traza)."""
    tot = {}
    for fase in ('llm', 'tests'):
        ms = [f['carbono'][fase] for f in filas if fase in f.get('carbono', {})]
        tot[fase] = {
            'n': len(ms),
            'duracion_s': sum(m['duracion_s'] for m in ms),
            'energia_kwh': sum(m['energia_kwh'] for m in ms),
            'energia_traza_kwh': sum(m['energia_traza_kwh'] for m in ms),
            'emisiones_traza_kg': sum(m['emisiones_traza_kg'] for m in ms),
            'pico_w': max((m['potencia_pico_w'] for m in ms), default=0.0),
        }
    tot['reposo_potencia_w'] = reposo['energia_kwh'] * 3.6e6 / reposo['duracion_s']
    return tot


def escribir_resumen(args, base, filas, salida_dir, reposo, meta_carbono):
    det = determinismo(filas, salida_dir)
    total = sum(f.get('costo_usd') or 0 for f in filas)
    tot = totales_carbono(filas, reposo)
    wh = lambda kwh: kwh * 1e3
    mg = lambda kg: kg * 1e6
    lineas = [
        '# Resumen de pruebas con LLM (prompt general) — Tornado', '',
        '- Python: `%s`' % sys.version.split()[0],
        '- SDK anthropic: `%s`' % anthropic.__version__,
        '- Modelo solicitado: `%s` (effort `%s`)' % (args.modelo, args.effort),
        '- Prompt: `%s`' % PROMPT.name,
        '- Corridas por módulo: %d' % args.corridas,
        '- Fecha: %s' % time.strftime('%Y-%m-%d %H:%M'),
        '- Costo total estimado: US$ %.2f' % total, '',
        '## Línea base', '',
        '%(ran)d tests: %(passed)d passed, %(failed)d failed, %(skipped)d skipped, '
        '%(errors)d errors' % base, '',
        '## Corridas', '',
        '| Corrida | Modelo | +/− líneas | Tests (passed/failed/errors) | Veredicto | Tipo de fallo | '
        'Cambios API pública | Tiempo (s) | Costo (US$) |',
        '|---|---|---|---|---|---|---|---|---|',
    ]
    for f in filas:
        t = f.get('tests')
        tests = '%d / %d / %d' % (t['passed'], t['failed'], t['errors']) if t else '—'
        lineas_diff = ('+%d / −%d' % (f['lineas_agregadas'], f['lineas_eliminadas'])
                       if 'lineas_agregadas' in f else '—')
        api = '; '.join(f.get('cambios_api_publica') or []) or '—'
        lineas.append('| %s | %s | %s | %s | **%s** | %s | %s | %s | %s |' % (
            f['id'], f.get('modelo_respuesta', '—'), lineas_diff, tests,
            f['veredicto'], f.get('tipo_fallo', ''), api, f.get('tiempo_llm_s', '—'),
            f.get('costo_usd', '—')))

    lineas += ['', '## Determinismo', '',
               '| Módulo | Corridas | Diffs distintos |', '|---|---|---|']
    for modulo, d in det.items():
        lineas.append('| %s | %d | %d |' % (modulo, d['corridas'], d['diffs_distintos']))

    lineas += [
        '', '## Huella de carbono local (CodeCarbon + traza continua de 0,1 s)', '',
        'Solo el consumo **de este equipo**. La llamada al LLM mide al Mac esperando '
        'la respuesta por red; la energía de los servidores de Anthropic no se puede '
        'medir desde aquí (por eso se registran los tokens).', '',
        '| Corrida | LLM: duración (s) | LLM: energía (Wh) | LLM: pico (W) | '
        'Tests: duración (s) | Tests: energía (Wh) | Tests: pico (W) | '
        'Emisiones locales (mg CO2eq) | Tokens salida |',
        '|---|---|---|---|---|---|---|---|---|']
    for f in filas:
        c = f.get('carbono', {})
        if 'llm' not in c:
            continue
        l, t = c['llm'], c.get('tests')
        em = l['emisiones_traza_kg'] + (t['emisiones_traza_kg'] if t else 0)
        lineas.append('| %s | %.1f | %.4f | %.1f | %s | %s | %s | %.3f | %s |' % (
            f['id'], l['duracion_s'], wh(l['energia_traza_kwh']), l['potencia_pico_w'],
            '%.1f' % t['duracion_s'] if t else '—',
            '%.4f' % wh(t['energia_traza_kwh']) if t else '—',
            '%.1f' % t['potencia_pico_w'] if t else '—', mg(em),
            f.get('tokens', {}).get('output', '—')))
    lineas += ['', '### Totales', '',
               '| Fase | n | Duración (s) | Energía traza (Wh) | Energía CodeCarbon (Wh) | '
               'Emisiones (mg CO2eq) |', '|---|---|---|---|---|---|']
    for fase, nombre in (('llm', 'Llamadas al LLM (espera local)'),
                         ('tests', 'Corridas de tests')):
        x = tot[fase]
        lineas.append('| %s | %d | %.1f | %.4f | %.4f | %.3f |' % (
            nombre, x['n'], x['duracion_s'], wh(x['energia_traza_kwh']),
            wh(x['energia_kwh']), mg(x['emisiones_traza_kg'])))
    lineas += ['', '- Reposo (%d s sin carga): potencia media %.2f W.'
               % (SEGUNDOS_REPOSO, tot['reposo_potencia_w']),
               '- CodeCarbon %s, país `%s`, CPU `%s` TDP %s W.'
               % (meta_carbono['codecarbon'], meta_carbono['pais'],
                  meta_carbono['cpu_modelo'], meta_carbono['cpu_tdp_w']), '',
               'Las refactorizaciones que el modelo dice haber aplicado están al final '
               'de cada `<corrida>_respuesta.md`.', '']
    (salida_dir / 'resumen.md').write_text('\n'.join(lineas))
    (salida_dir / 'resumen.json').write_text(json.dumps(
        {'python': sys.version.split()[0], 'anthropic': anthropic.__version__,
         'modelo': args.modelo, 'effort': args.effort, 'prompt': PROMPT.read_text(),
         'linea_base': base, 'determinismo': det, 'costo_total_usd': round(total, 4),
         'reposo': reposo, 'codecarbon': meta_carbono, 'carbono_totales': tot,
         'corridas': filas},
        indent=2, ensure_ascii=False))


def metadatos_carbono(medidor):
    import codecarbon
    cpu = next((h for h in medidor._hardware if type(h).__name__ == 'CPU'), None)
    return {'codecarbon': codecarbon.__version__, 'pais': PAIS,
            'modo_cpu': getattr(cpu, '_mode', None),
            'cpu_modelo': getattr(cpu, '_model', None),
            'cpu_tdp_w': getattr(cpu, '_tdp', None)}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--modelo', default='claude-sonnet-5-5')
    parser.add_argument('--effort', default='high',
                        choices=['low', 'medium', 'high', 'xhigh', 'max'])
    parser.add_argument('--corridas', type=int, default=3)
    parser.add_argument('--max-tokens', type=int, default=128000)
    parser.add_argument('--modulos', nargs='+', default=MODULOS_POR_DEFECTO, choices=MODULOS)
    parser.add_argument('--dry-run', action='store_true',
                        help='muestra el prompt y cuenta los tokens, sin generar nada')
    parser.add_argument('--reanudar', metavar='CARPETA',
                        help='continúa una ejecución interrumpida en resultados/CARPETA')
    args = parser.parse_args()

    sistema = PROMPT.read_text()
    contexto = contexto_paquete()
    if args.dry_run:
        print('=== SYSTEM ===\n%s\n=== USER (%d caracteres, %d módulos) ===\n%s\n...'
              % (sistema, len(contexto), len(MODULOS), contexto[:300]))
        n = anthropic.Anthropic().messages.count_tokens(
            model=args.modelo, system=sistema,
            messages=[{'role': 'user', 'content': contexto + '\n\nRefactoriza `tornado/web.py`.'}])
        print('Tokens de entrada por llamada: %d' % n.input_tokens)
        return

    verificar_sin_tornado_instalado()
    cliente = anthropic.Anthropic()
    filas = []
    if args.reanudar:
        salida_dir = RESULTADOS / args.reanudar
        previo = json.loads((salida_dir / 'resumen.json').read_text())
        assert previo['prompt'] == sistema, 'el prompt cambió desde la ejecución original'
        assert (previo['modelo'], previo['effort']) == (args.modelo, args.effort)
        filas = [f for f in previo['corridas'] if not f['veredicto'].startswith('ERROR')]
        print('[reanudar] %d corridas ya hechas en %s' % (len(filas), salida_dir))
    else:
        salida_dir = RESULTADOS / time.strftime('%Y%m%d_%H%M%S')
        salida_dir.mkdir(parents=True)
        (salida_dir / 'prompt.md').write_text(sistema)
    hechas = {f['id'] for f in filas}

    medidor = Medidor(PAIS, TDP_CPU_W, MEDICIONES, 'tornado_llm')
    if args.reanudar:
        reposo = previo['reposo']
    else:
        medidor.medir('reposo', '00_reposo', lambda: time.sleep(SEGUNDOS_REPOSO))
        reposo = MEDICIONES[-1]
    meta_carbono = metadatos_carbono(medidor)

    carpeta = copia_limpia('00_linea_base')
    base, salida = medidor.medir('tests', '00_linea_base', lambda: correr_tests(carpeta))
    (salida_dir / '00_linea_base_tests.txt').write_text(salida)
    print('[linea base] %s' % base)
    medidor.guardar_traza(salida_dir / 'traza_carbono.csv', anexar=True)

    for modulo in args.modulos:
        for n in range(1, args.corridas + 1):
            if '%s_run%d' % (modulo, n) in hechas:
                continue
            filas.append(corrida(cliente, medidor, args, sistema, contexto, modulo, n,
                                 base, salida_dir))
            medidor.guardar_traza(salida_dir / 'traza_carbono.csv', anexar=True)
            escribir_resumen(args, base, filas, salida_dir, reposo, meta_carbono)
    print('\nResultados en %s' % salida_dir)


if __name__ == '__main__':
    main()
