"""Pruebas de Tornado con Rope (refactorización automática) + huella de carbono.

Réplica del experimento hecho sobre PySnooper (../PySnooper_tesis/rope_pruebas)
y Cookiecutter (../cookiecutter_tesis/rope_pruebas), con los mismos tipos de
refactorización y la misma numeración (02-12), más ocho casos propios de
Tornado (13-20).

Flujo:
  0. Reposo: mide con CodeCarbon el consumo del equipo sin hacer nada
     (referencia de ruido de fondo).
  1. Línea base: corre la suite de tests original de Tornado (3 veces, para
     ver la variabilidad del consumo).
  2. Análisis estático con Rope (sin modificar código): find_errors,
     find_occurrences y find_definition.
  3. Refactorizaciones: cada una se aplica con la API de Rope sobre una
     copia limpia del proyecto, se guarda el diff y se vuelve a correr la
     suite de tests. Si los tests siguen pasando, la refactorización
     preservó el comportamiento.

Cada fase se mide con CodeCarbon (una "task" por fase): duración, energía
(kWh) y emisiones (kg CO2eq). La operación de Rope se repite
REPETICIONES_ROPE veces, cada una sobre una copia limpia, para obtener media
y desviación estándar.

El código original en ../tornado NUNCA se modifica.

Uso (desde la raíz del repositorio):
    .venv/bin/python rope_pruebas/ejecutar_pruebas_rope.py
"""
import csv
import json
import logging
import os
import platform
import re
import shutil
import statistics
import subprocess
import sys
import time
import traceback
from pathlib import Path

import codecarbon
import rope
from codecarbon import OfflineEmissionsTracker
from rope.base.project import Project
from rope.contrib import findit, finderrors
from rope.refactor.extract import ExtractMethod
from rope.refactor.inline import create_inline
from rope.refactor.move import create_move
from rope.refactor.rename import Rename

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parent
TRABAJO = AQUI / '_trabajo'
RESULTADOS = AQUI / 'resultados'
PYTHON = sys.executable

# País de la red eléctrica para el factor de emisión (código ISO 3166-1 alfa-3).
PAIS = os.environ.get('CODECARBON_PAIS', 'COL')
# TDP del CPU en vatios. CodeCarbon 3.3.2 no logra asociar "Apple M4" con su
# propia tabla (empata con M4 Pro/Max/Ultra y descarta el resultado) y usa un
# valor genérico de 10 hilos x 8,5 W = 85 W. Se fuerza el valor que la misma
# tabla de CodeCarbon (data/hardware/cpu_power.csv) da para el Apple M4.
TDP_CPU_W = float(os.environ.get('CODECARBON_TDP', '20'))
TDP_GENERICO_W = 85.0
REPETICIONES_ROPE = 5
REPETICIONES_BASE = 3
SEGUNDOS_REPOSO = 20

IGNORAR = shutil.ignore_patterns(
    '.git', '.github', '.venv', '*.egg-info', '__pycache__', '.ropeproject',
    '.mypy_cache', '.tox', 'build', 'rope_pruebas', 'docs', 'demos', 'maint',
)


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def copia_limpia(nombre):
    """Copia el repositorio (sin .git/.venv/docs/demos) a _trabajo/<nombre>."""
    destino = TRABAJO / nombre
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(REPO, destino, ignore=IGNORAR)
    return destino


def entorno(carpeta):
    """Variables de entorno para que se importe el tornado de la copia.

    El .venv tiene tornado instalado en modo editable apuntando al
    repositorio original; PYTHONPATH va antes en sys.path y lo tapa. Los
    subprocesos que lanzan los propios tests (import_test, autoreload_test,
    process_test) heredan la variable.
    """
    env = dict(os.environ)
    env['PYTHONPATH'] = str(carpeta)
    return env


def correr_tests(carpeta):
    """Corre la suite oficial de Tornado y devuelve (resumen, salida completa).

    Tornado no usa pytest: su runner es unittest (`python -m
    tornado.test.runtests`). La última línea tiene la forma
    `OK (skipped=111)` o `FAILED (failures=2, errors=1, skipped=111)`.
    """
    proc = subprocess.run(
        [PYTHON, '-m', 'tornado.test.runtests'],
        cwd=carpeta, capture_output=True, text=True, env=entorno(carpeta),
    )
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
        # El runner ni siquiera llegó a ejecutar tests (p. ej. un ImportError
        # en tornado.test.runtests). Se cuenta como un error.
        resumen['errors'] = max(resumen['errors'], 1)
    resumen['ran'] = ejecutados
    resumen['passed'] = (ejecutados - resumen['failed'] - resumen['errors']
                         - resumen['skipped'] - resumen['expected_failures'])
    resumen['passed'] = max(resumen['passed'], 0)
    return resumen, salida


def verificar_import(carpeta):
    """Confirma que se importa el tornado de la copia, no otro."""
    proc = subprocess.run(
        [PYTHON, '-c', 'import tornado; print(tornado.__file__)'],
        cwd=carpeta, capture_output=True, text=True, env=entorno(carpeta),
    )
    ruta = proc.stdout.strip()
    assert ruta.startswith(str(carpeta)), ruta
    return ruta


def abrir_proyecto(carpeta):
    """Abre la copia como proyecto Rope (misma opción que en Cookiecutter)."""
    return Project(str(carpeta), ignore_syntax_errors=True)


def offset_de(recurso, marcador, desplazamiento=0):
    """Offset (en caracteres) de `marcador` dentro del archivo."""
    codigo = recurso.read()
    assert codigo.count(marcador) == 1, 'marcador ambiguo o ausente: %r' % marcador
    return codigo.index(marcador) + desplazamiento


def inicio_de_linea(recurso, marcador):
    codigo = recurso.read()
    return codigo.rfind('\n', 0, offset_de(recurso, marcador)) + 1


def linea_anterior(recurso, offset):
    """Inicio de la línea anterior a `offset` (para excluir una línea en blanco)."""
    return recurso.read().rfind('\n', 0, offset - 1) + 1


# ---------------------------------------------------------------------------
# Medición de carbono (CodeCarbon)
# ---------------------------------------------------------------------------

MEDICIONES = []


def crear_tracker():
    """Un solo tracker para todo el experimento; cada fase es una "task".

    - Offline: no envía datos a internet; el factor de emisión sale de la
      tabla de CodeCarbon para el país PAIS.
    - measure_power_secs=1: muestrea la carga de CPU cada segundo.
    - tracking_mode='machine': mide la carga de TODO el equipo. Es necesario
      porque los tests corren en un subproceso (en modo 'process' solo se
      contaría el proceso de este script).
    - force_cpu_power + force_mode_cpu_load: ver TDP_CPU_W. Sin sudo no hay
      acceso a `powermetrics`, así que en macOS la única opción es estimar
      P_cpu = TDP * (0.1 + 0.9 * carga^3).
    """
    logging.getLogger('codecarbon').setLevel(logging.ERROR)
    return OfflineEmissionsTracker(
        country_iso_code=PAIS, project_name='tornado_rope',
        measure_power_secs=1, tracking_mode='machine',
        force_cpu_power=TDP_CPU_W, force_mode_cpu_load=True,
        save_to_file=False, log_level='error',
    )


def medir(tracker, fase, experimento, funcion, repeticion=1):
    """Ejecuta funcion() dentro de una task de CodeCarbon y anota el consumo."""
    tracker.start_task('%s:%s:%d' % (experimento, fase, repeticion))
    try:
        return funcion()
    finally:
        d = tracker.stop_task()
        MEDICIONES.append({
            'experimento': experimento, 'fase': fase, 'repeticion': repeticion,
            'duracion_s': d.duration,
            'energia_kwh': d.energy_consumed,
            'energia_cpu_kwh': d.cpu_energy,
            'energia_ram_kwh': d.ram_energy,
            'emisiones_kg': d.emissions,
            'potencia_cpu_w': d.cpu_power,
            'potencia_ram_w': d.ram_power,
        })


def metadatos_tracker(tracker):
    """Datos del hardware que usa CodeCarbon (llamar después de la 1.ª task,
    que es cuando CodeCarbon termina de detectar el hardware)."""
    cpu = next((h for h in tracker._hardware if type(h).__name__ == 'CPU'), None)
    return {
        'codecarbon': codecarbon.__version__,
        'pais': PAIS,
        'modo_cpu': getattr(cpu, '_mode', None),
        'cpu_modelo': getattr(cpu, '_model', None),
        'cpu_tdp_w': getattr(cpu, '_tdp', None),
        'cpu_tdp_generico': getattr(cpu, '_is_generic_tdp', None),
        'ram_potencia_w': MEDICIONES[0]['potencia_ram_w'] if MEDICIONES else None,
        'tracking_mode': 'machine',
        'plataforma': platform.platform(),
    }


# ---------------------------------------------------------------------------
# 0 y 1. Reposo y línea base
# ---------------------------------------------------------------------------

def reposo(tracker):
    medir(tracker, 'reposo', '00_reposo', lambda: time.sleep(SEGUNDOS_REPOSO))
    m = MEDICIONES[-1]
    print('[reposo] %.1f s  %.3e kWh  %.3e kg CO2eq'
          % (m['duracion_s'], m['energia_kwh'], m['emisiones_kg']))


def linea_base(tracker):
    carpeta = copia_limpia('00_linea_base')
    ruta = verificar_import(carpeta)
    for i in range(1, REPETICIONES_BASE + 1):
        resumen, salida = medir(tracker, 'tests', '00_linea_base',
                                lambda: correr_tests(carpeta), repeticion=i)
        print('[linea base %d/%d] %s  (tornado importado desde %s)'
              % (i, REPETICIONES_BASE, resumen, ruta))
    (RESULTADOS / '00_linea_base_tests.txt').write_text(salida)
    return resumen


# ---------------------------------------------------------------------------
# 2. Análisis estático
# ---------------------------------------------------------------------------

SIMBOLOS = [
    # (archivo, marcador, desplazamiento hasta el nombre)
    ('tornado/httputil.py', 'def url_concat', 4),
    ('tornado/netutil.py', 'def is_valid_ip', 4),
    ('tornado/util.py', 'class Configurable:', 6),
    ('tornado/iostream.py', 'def _try_inline_read', 4),
    ('tornado/httputil.py', 'def _normalize_header', 4),
    ('tornado/httputil.py', 'def doctests', 4),
]


def analisis_estatico():
    carpeta = copia_limpia('01_analisis')
    proyecto = abrir_proyecto(carpeta)
    lineas = ['# Análisis estático con Rope %s' % rope.VERSION, '']

    lineas += ['## find_errors (rope.contrib.finderrors)', '',
               '| Módulo | Errores reportados |', '|---|---|']
    errores_totales = []
    modulos = sorted((carpeta / 'tornado').glob('*.py')) + \
        sorted((carpeta / 'tornado' / 'platform').glob('*.py'))
    for archivo in modulos:
        rel = archivo.relative_to(carpeta).as_posix()
        errores = finderrors.find_errors(proyecto, proyecto.get_resource(rel))
        errores_totales += [(rel, e.lineno, e.error) for e in errores]
        lineas.append('| `%s` | %d |' % (rel, len(errores)))
    lineas.append('')
    for rel, lineno, error in errores_totales:
        lineas.append('- `%s:%d` — %s' % (rel, lineno, error))
    if errores_totales:
        lineas.append('')

    lineas += ['## find_occurrences (rope.contrib.findit)', '']
    ocurrencias = {}
    for rel, marcador, desp in SIMBOLOS:
        recurso = proyecto.get_resource(rel)
        offset = offset_de(recurso, marcador, desp)
        nombre = re.match(r'\w+', recurso.read()[offset:]).group(0)
        encontradas = findit.find_occurrences(proyecto, recurso, offset)
        ocurrencias[nombre] = len(encontradas)
        lineas.append('### `%s` (%d ocurrencias)' % (nombre, len(encontradas)))
        lineas.append('')
        for o in encontradas:
            lineas.append('- `%s:%d`%s' % (o.resource.path, o.lineno,
                                          ' (dudosa)' if o.unsure else ''))
        lineas.append('')

    lineas += ['## find_definition (rope.contrib.findit)', '']
    recurso = proyecto.get_resource('tornado/auth.py')
    offset = offset_de(recurso, 'return url_concat(url, args)', 7)
    definicion = findit.find_definition(proyecto, recurso.read(), offset, recurso)
    lineas.append('Desde `tornado/auth.py` (`return url_concat(url, args)`) '
                  'Rope resuelve la definición en `%s:%d`.'
                  % (definicion.resource.path, definicion.lineno))
    lineas.append('')

    proyecto.close()
    (RESULTADOS / '01_analisis_estatico.md').write_text('\n'.join(lineas))
    print('[analisis] errores=%d ocurrencias=%s' % (len(errores_totales), ocurrencias))
    return {'errores': len(errores_totales), 'ocurrencias': ocurrencias,
            'definicion': '%s:%d' % (definicion.resource.path, definicion.lineno)}


# ---------------------------------------------------------------------------
# 3. Refactorizaciones
# ---------------------------------------------------------------------------
# Cada función recibe el proyecto Rope y devuelve un objeto ChangeSet.

def ref_rename_funcion(p):
    r = p.get_resource('tornado/httputil.py')
    return Rename(p, r, offset_de(r, 'def url_concat', 4)).get_changes('concat_url_args')


def ref_rename_funcion_importada(p):
    r = p.get_resource('tornado/netutil.py')
    return Rename(p, r, offset_de(r, 'def is_valid_ip', 4)).get_changes('is_ip_address')


def ref_rename_metodo(p):
    r = p.get_resource('tornado/iostream.py')
    return Rename(p, r, offset_de(r, 'def _maybe_add_error_listener', 4)).get_changes('_ensure_error_listener')


def ref_rename_clase(p):
    r = p.get_resource('tornado/util.py')
    return Rename(p, r, offset_de(r, 'class Configurable:', 6)).get_changes('ConfigurableBase')


def ref_rename_parametro(p):
    # Los llamadores pasan el parámetro por nombre (url_escape(x, plus=False)).
    # url_unescape tiene un parámetro con el mismo nombre que NO debe cambiar.
    r = p.get_resource('tornado/escape.py')
    return Rename(p, r, offset_de(r, 'def url_escape(value: str | bytes, plus', 35)).get_changes('use_plus')


def ref_extract_boundary(p):
    # Bloque de parse_multipart_form_data que quita las comillas del boundary
    # (reasigna un parámetro: 1 valor de salida).
    r = p.get_resource('tornado/httputil.py')
    inicio = inicio_de_linea(r, '''    if boundary.startswith(b'"') and boundary.endswith(b'"'):''')
    fin = inicio_de_linea(r, '    final_boundary_index = data.rfind(')
    return ExtractMethod(p, r, inicio, fin).get_changes('_unquote_boundary')


def ref_extract_rango(p):
    # Primeras dos líneas de _parse_request_range: producen 2 valores de
    # salida (unit y value) y una variable descartable `_`.
    r = p.get_resource('tornado/httputil.py')
    inicio = inicio_de_linea(r, '    unit, _, value = range_header.partition("=")')
    fin = inicio_de_linea(r, '    if unit != "bytes":\n        return None')
    return ExtractMethod(p, r, inicio, fin).get_changes('_split_range_header')


def ref_extract_con_return(p):
    # try/except de _parse_request_range con `return None` en medio de la
    # función: caso límite (flujo de control que sale de la función).
    r = p.get_resource('tornado/httputil.py')
    inicio = inicio_de_linea(r, '    try:\n        start = _int_or_none(start_b)')
    fin = inicio_de_linea(r, '    if end is not None:\n        if start is None:')
    return ExtractMethod(p, r, inicio, fin).get_changes('_parse_range_bounds')


def ref_extract_bucle(p):
    # Bucle de parse_body_arguments que copia los argumentos urlencoded
    # (lee 2 variables locales, no produce valores de salida).
    r = p.get_resource('tornado/httputil.py')
    inicio = inicio_de_linea(r, '        for name, values in uri_arguments.items():')
    fin = inicio_de_linea(r, '    elif content_type.startswith("multipart/form-data"):')
    return ExtractMethod(p, r, inicio, fin).get_changes('_merge_urlencoded_arguments')


def ref_inline_funcion(p):
    # _int_or_none reasigna su parámetro y tiene 2 return (mismo patrón que
    # el Inline que falló en Cookiecutter).
    r = p.get_resource('tornado/httputil.py')
    return create_inline(p, r, offset_de(r, 'def _int_or_none', 4)).get_changes()


def ref_move_funcion(p):
    # _format_addr se usa en tcpclient y los tests la importan desde ahí.
    r = p.get_resource('tornado/tcpclient.py')
    destino = p.get_resource('tornado/netutil.py')
    return create_move(p, r, offset_de(r, 'def _format_addr', 4)).get_changes(destino)


def ref_rename_parcheada(p):
    # iostream_test hace mock.patch("tornado.iostream.BaseIOStream._try_inline_read"):
    # la referencia está en un string y Rope no la ve.
    r = p.get_resource('tornado/iostream.py')
    return Rename(p, r, offset_de(r, 'def _try_inline_read', 4)).get_changes('_read_inline_if_possible')


def ref_rename_con_doctest(p):
    # _normalize_header tiene un doctest en su propio docstring:
    #     >>> _normalize_header("coNtent-TYPE")
    # Los doctests de httputil se ejecutan como parte de la suite.
    r = p.get_resource('tornado/httputil.py')
    return Rename(p, r, offset_de(r, 'def _normalize_header', 4)).get_changes('_to_header_case')


def ref_rename_con_doctest_docs(p):
    # Igual que 14, con docs=True (renombra también en strings y comentarios
    # donde el nombre es visible).
    r = p.get_resource('tornado/httputil.py')
    return Rename(p, r, offset_de(r, 'def _normalize_header', 4)).get_changes('_to_header_case', docs=True)


def ref_rename_en_test_modules(p):
    # runtests.TEST_MODULES lista "tornado.httputil.doctests" como string.
    r = p.get_resource('tornado/httputil.py')
    return Rename(p, r, offset_de(r, 'def doctests', 4)).get_changes('doctest_suite')


def ref_rename_verbo_http(p):
    # RequestHandler._execute despacha con getattr(self, method.lower()):
    # el nombre del método `get` ES el verbo HTTP.
    r = p.get_resource('tornado/test/web_test.py')
    return Rename(p, r, offset_de(r, 'class HelloHandler(RequestHandler):\n    def get', 44)).get_changes('handle_get')


def ref_rename_handler_por_string(p):
    # web_test registra rutas con el handler como string:
    #     ("/hello2", "tornado.test.web_test.HelloHandler")
    # Application lo resuelve con import_object en tiempo de ejecución.
    r = p.get_resource('tornado/test/web_test.py')
    return Rename(p, r, offset_de(r, 'class HelloHandler(', 6)).get_changes('GreetingHandler')


def ref_rename_modulo(p):
    # Renombrar el módulo tornado/locks.py -> tornado/sync.py. tornado/__init__.py
    # lista los submódulos como strings en __all__ (import perezoso, PEP 562)
    # y tornado/__init__.pyi los importa en un stub.
    r = p.get_resource('tornado/locks.py')
    return Rename(p, r).get_changes('sync')


def ref_extract_await(p):
    # Bloque de RequestHandler._execute (async def) que llama a prepare() y
    # hace `await` del resultado.
    r = p.get_resource('tornado/web.py')
    inicio = inicio_de_linea(r, '            result = self.prepare()')
    fin = inicio_de_linea(r, '            if self._prepared_future is not None:\n                # Tell the Application')
    return ExtractMethod(p, r, inicio, fin).get_changes('_run_prepare')


REFACTORIZACIONES = [
    ('02_rename_funcion', 'Rename', 'httputil.url_concat -> concat_url_args (usada en auth, httpclient y tests)', ref_rename_funcion),
    ('03_rename_funcion_importada', 'Rename', 'netutil.is_valid_ip -> is_ip_address (también importada por caresresolver y los tests)', ref_rename_funcion_importada),
    ('04_rename_metodo', 'Rename', 'BaseIOStream._maybe_add_error_listener -> _ensure_error_listener', ref_rename_metodo),
    ('05_rename_clase', 'Rename', 'util.Configurable -> ConfigurableBase (clase base de IOLoop, AsyncHTTPClient y Resolver)', ref_rename_clase),
    ('06_rename_parametro', 'Rename', 'parámetro plus de escape.url_escape -> use_plus (los llamadores lo pasan por nombre)', ref_rename_parametro),
    ('07_extract_boundary', 'Extract Method', 'quitar comillas del boundary en parse_multipart_form_data -> _unquote_boundary', ref_extract_boundary),
    ('08_extract_rango', 'Extract Method', 'separar unidad y valor en _parse_request_range -> _split_range_header (2 valores de salida)', ref_extract_rango),
    ('09_extract_con_return', 'Extract Method', 'try/except con `return None` de _parse_request_range -> _parse_range_bounds (caso límite)', ref_extract_con_return),
    ('10_extract_bucle', 'Extract Method', 'bucle que copia argumentos urlencoded en parse_body_arguments -> _merge_urlencoded_arguments', ref_extract_bucle),
    ('11_inline_funcion', 'Inline', 'inline de httputil._int_or_none en _parse_request_range (2 llamadas; reasigna su parámetro y tiene 2 return)', ref_inline_funcion),
    ('12_move_funcion', 'Move', 'mover tcpclient._format_addr a netutil (los tests la importan)', ref_move_funcion),
    ('13_rename_parcheada', 'Rename', 'BaseIOStream._try_inline_read -> _read_inline_if_possible (los tests la parchean con mock.patch("tornado.iostream.BaseIOStream._try_inline_read"))', ref_rename_parcheada),
    ('14_rename_con_doctest', 'Rename', 'httputil._normalize_header -> _to_header_case (tiene un doctest en su docstring)', ref_rename_con_doctest),
    ('15_rename_con_doctest_docs', 'Rename', 'igual que 14 pero con docs=True', ref_rename_con_doctest_docs),
    ('16_rename_en_test_modules', 'Rename', 'httputil.doctests -> doctest_suite (runtests.TEST_MODULES la nombra como string)', ref_rename_en_test_modules),
    ('17_rename_verbo_http', 'Rename', 'método get de HelloHandler -> handle_get (Tornado despacha con getattr(self, método_http))', ref_rename_verbo_http),
    ('18_rename_handler_string', 'Rename', 'clase HelloHandler -> GreetingHandler (las rutas la nombran como string "tornado.test.web_test.HelloHandler")', ref_rename_handler_por_string),
    ('19_rename_modulo', 'Rename (módulo)', 'módulo tornado/locks.py -> tornado/sync.py (tornado.__all__ lo nombra como string)', ref_rename_modulo),
    ('20_extract_await', 'Extract Method', 'bloque con `await` de RequestHandler._execute (async def) -> _run_prepare', ref_extract_await),
]


def aplicar_rope(nombre, funcion, repeticion, tracker):
    """Aplica la refactorización en una copia limpia. Devuelve (carpeta, cambios, error)."""
    carpeta = copia_limpia(nombre)
    proyecto = abrir_proyecto(carpeta)

    def operacion():
        cambios = funcion(proyecto)
        proyecto.do(cambios)
        return cambios

    try:
        cambios = medir(tracker, 'rope', nombre, operacion, repeticion)
        return carpeta, cambios, None
    except Exception as e:
        return carpeta, None, (e, traceback.format_exc())
    finally:
        proyecto.close()


def aplicar(nombre, tipo, descripcion, funcion, base, tracker):
    fila = {'id': nombre, 'tipo': tipo, 'descripcion': descripcion}
    for i in range(1, REPETICIONES_ROPE + 1):
        carpeta, cambios, error = aplicar_rope(nombre, funcion, i, tracker)
        if error:
            break
    tiempos = [m['duracion_s'] for m in MEDICIONES
               if m['experimento'] == nombre and m['fase'] == 'rope']
    fila['tiempo_rope_s'] = round(statistics.mean(tiempos), 3)
    if error:
        e, tb = error
        fila['estado_rope'] = 'error: %s: %s' % (type(e).__name__, e)
        fila['veredicto'] = 'RECHAZADA POR ROPE'
        (RESULTADOS / (nombre + '_error.txt')).write_text(tb)
        print('[%s] Rope rechazó: %s' % (nombre, fila['estado_rope']))
        return fila
    fila['estado_rope'] = 'aplicada'
    fila['archivos_modificados'] = sorted(r.path for r in cambios.get_changed_resources())
    (RESULTADOS / (nombre + '.diff')).write_text(cambios.get_description())

    resumen, salida = medir(tracker, 'tests', nombre, lambda: correr_tests(carpeta))
    (RESULTADOS / (nombre + '_tests.txt')).write_text(salida)
    fila['tests'] = resumen
    igual = (resumen['passed'] == base['passed'] and resumen['failed'] == 0
             and resumen['errors'] == 0)
    fila['veredicto'] = 'COMPORTAMIENTO PRESERVADO' if igual else 'ROMPE TESTS'
    print('[%s] %s  %s' % (nombre, fila['veredicto'], resumen))
    return fila


# ---------------------------------------------------------------------------
# Reporte
# ---------------------------------------------------------------------------

def agregados_carbono():
    """Totales y medias por fase a partir de MEDICIONES."""
    def suma(filtro, campo):
        return sum(m[campo] for m in MEDICIONES if filtro(m))

    reposo_m = next(m for m in MEDICIONES if m['fase'] == 'reposo')
    base_m = [m for m in MEDICIONES if m['experimento'] == '00_linea_base']
    rope_m = [m for m in MEDICIONES if m['fase'] == 'rope']
    tests_ref = [m for m in MEDICIONES if m['fase'] == 'tests'
                 and m['experimento'] != '00_linea_base']

    def stats(ms, campo):
        valores = [m[campo] for m in ms]
        return {'media': statistics.mean(valores),
                'desv': statistics.stdev(valores) if len(valores) > 1 else 0.0,
                'min': min(valores), 'max': max(valores), 'n': len(valores)}

    return {
        'reposo': {
            'duracion_s': reposo_m['duracion_s'],
            'potencia_media_w': reposo_m['energia_kwh'] * 3.6e6 / reposo_m['duracion_s'],
            'emisiones_kg': reposo_m['emisiones_kg'],
        },
        'factor_emision_kg_por_kwh': (reposo_m['emisiones_kg'] / reposo_m['energia_kwh']
                                      if reposo_m['energia_kwh'] else None),
        'linea_base_tests': {c: stats(base_m, c) for c in
                             ('duracion_s', 'energia_kwh', 'emisiones_kg')},
        'rope_por_operacion': {c: stats(rope_m, c) for c in
                               ('duracion_s', 'energia_kwh', 'emisiones_kg')},
        'total_rope': {c: suma(lambda m: m['fase'] == 'rope', c)
                       for c in ('duracion_s', 'energia_kwh', 'emisiones_kg')},
        'total_analisis': {c: suma(lambda m: m['fase'] == 'analisis', c)
                           for c in ('duracion_s', 'energia_kwh', 'emisiones_kg')},
        'total_tests': {c: sum(m[c] for m in base_m + tests_ref)
                        for c in ('duracion_s', 'energia_kwh', 'emisiones_kg')},
        'total_experimento': {c: suma(lambda m: m['fase'] != 'reposo', c)
                              for c in ('duracion_s', 'energia_kwh', 'emisiones_kg')},
        # En el modelo cpu_load la energía de CPU es proporcional al TDP, así
        # que se puede recalcular qué habría reportado CodeCarbon con su TDP
        # genérico de 85 W (sin la corrección de TDP_CPU_W).
        'sensibilidad_tdp_generico': {
            'tdp_w': TDP_GENERICO_W,
            'energia_kwh': suma(lambda m: m['fase'] != 'reposo', 'energia_cpu_kwh')
            * TDP_GENERICO_W / TDP_CPU_W
            + suma(lambda m: m['fase'] != 'reposo', 'energia_ram_kwh'),
        },
    }


def escribir_resumen(base, analisis, filas, meta, carbono):
    mg = lambda kg: kg * 1e6          # kg -> mg
    wh = lambda kwh: kwh * 1e3        # kWh -> Wh
    lineas = [
        '# Resumen de pruebas con Rope (Tornado)', '',
        '- Python: `%s`' % sys.version.split()[0],
        '- Rope: `%s`' % rope.VERSION,
        '- CodeCarbon: `%s` (modo offline, país `%s`, CPU `%s` TDP %s W, RAM %s W)'
        % (meta['codecarbon'], meta['pais'], meta['cpu_modelo'], meta['cpu_tdp_w'],
           meta['ram_potencia_w']),
        '- Fecha: %s' % time.strftime('%Y-%m-%d %H:%M'), '',
        '## Línea base', '',
        '%(ran)d tests: %(passed)d passed, %(failed)d failed, %(skipped)d skipped, '
        '%(errors)d errors' % base, '',
        '## Refactorizaciones', '',
        '| # | Tipo | Descripción | Rope | Tiempo Rope (s, media de %d) | '
        'Tests (passed/failed/errors) | Veredicto |' % REPETICIONES_ROPE,
        '|---|---|---|---|---|---|---|',
    ]
    for f in filas:
        t = f.get('tests')
        tests = '%d / %d / %d' % (t['passed'], t['failed'], t['errors']) if t else '—'
        lineas.append('| %s | %s | %s | %s | %s | %s | **%s** |' % (
            f['id'], f['tipo'], f['descripcion'], f['estado_rope'],
            f['tiempo_rope_s'], tests, f['veredicto']))

    lineas += ['', '## Huella de carbono (CodeCarbon)', '',
               '| Experimento | Fase | Duración (s) | Energía (Wh) | Emisiones (mg CO2eq) |',
               '|---|---|---|---|---|']
    agrupado = {}
    for m in MEDICIONES:
        clave = (m['experimento'], m['fase'])
        agrupado.setdefault(clave, []).append(m)
    for (exp, fase), ms in agrupado.items():
        n = len(ms)
        dur = statistics.mean(m['duracion_s'] for m in ms)
        en = statistics.mean(m['energia_kwh'] for m in ms)
        em = statistics.mean(m['emisiones_kg'] for m in ms)
        sufijo = ' (media de %d)' % n if n > 1 else ''
        lineas.append('| %s | %s%s | %.3f | %.4f | %.3f |'
                      % (exp, fase, sufijo, dur, wh(en), mg(em)))
    c = carbono
    lineas += [
        '', '### Totales', '',
        '| Concepto | Duración (s) | Energía (Wh) | Emisiones (mg CO2eq) |',
        '|---|---|---|---|',
        '| Todas las operaciones de Rope (%d) | %.2f | %.4f | %.3f |'
        % (c['rope_por_operacion']['duracion_s']['n'], c['total_rope']['duracion_s'],
           wh(c['total_rope']['energia_kwh']), mg(c['total_rope']['emisiones_kg'])),
        '| Análisis estático | %.2f | %.4f | %.3f |'
        % (c['total_analisis']['duracion_s'], wh(c['total_analisis']['energia_kwh']),
           mg(c['total_analisis']['emisiones_kg'])),
        '| Todas las corridas de tests | %.2f | %.4f | %.3f |'
        % (c['total_tests']['duracion_s'], wh(c['total_tests']['energia_kwh']),
           mg(c['total_tests']['emisiones_kg'])),
        '| **Experimento completo** (sin reposo) | %.2f | %.4f | %.3f |'
        % (c['total_experimento']['duracion_s'], wh(c['total_experimento']['energia_kwh']),
           mg(c['total_experimento']['emisiones_kg'])),
        '',
        '- Reposo (%d s sin carga): potencia media %.2f W.'
        % (SEGUNDOS_REPOSO, c['reposo']['potencia_media_w']),
        '- Factor de emisión usado: %.1f g CO2eq/kWh.'
        % (c['factor_emision_kg_por_kwh'] * 1e3),
        '- Sensibilidad: con el TDP genérico de %.0f W que CodeCarbon usa por defecto en '
        'este equipo, el experimento completo habría reportado %.4f Wh y %.3f mg CO2eq.'
        % (TDP_GENERICO_W, wh(c['sensibilidad_tdp_generico']['energia_kwh']),
           mg(c['sensibilidad_tdp_generico']['energia_kwh'] * c['factor_emision_kg_por_kwh'])),
        '- Una operación de Rope: media %.3f s, %.4f Wh, %.3f mg CO2eq (desv. %.3f mg).'
        % (c['rope_por_operacion']['duracion_s']['media'],
           wh(c['rope_por_operacion']['energia_kwh']['media']),
           mg(c['rope_por_operacion']['emisiones_kg']['media']),
           mg(c['rope_por_operacion']['emisiones_kg']['desv'])),
        '- Una corrida de la suite (línea base): media %.2f s, %.4f Wh, %.3f mg CO2eq (desv. %.3f mg).'
        % (c['linea_base_tests']['duracion_s']['media'],
           wh(c['linea_base_tests']['energia_kwh']['media']),
           mg(c['linea_base_tests']['emisiones_kg']['media']),
           mg(c['linea_base_tests']['emisiones_kg']['desv'])),
        '',
    ]
    (RESULTADOS / 'resumen.md').write_text('\n'.join(lineas))
    (RESULTADOS / 'resumen.json').write_text(json.dumps(
        {'python': sys.version.split()[0], 'rope': rope.VERSION,
         'codecarbon': meta, 'linea_base': base, 'analisis': analisis,
         'refactorizaciones': filas, 'carbono': carbono},
        indent=2, ensure_ascii=False))
    with open(RESULTADOS / 'carbono.csv', 'w', newline='') as f:
        escritor = csv.DictWriter(f, fieldnames=list(MEDICIONES[0]))
        escritor.writeheader()
        escritor.writerows(MEDICIONES)


def main():
    RESULTADOS.mkdir(exist_ok=True)
    for viejo in RESULTADOS.iterdir():
        viejo.unlink()
    tracker = crear_tracker()
    reposo(tracker)
    meta = metadatos_tracker(tracker)
    print('[codecarbon] %s' % meta)
    base = linea_base(tracker)
    analisis = medir(tracker, 'analisis', '01_analisis', analisis_estatico)
    filas = [aplicar(*r, base=base, tracker=tracker) for r in REFACTORIZACIONES]
    carbono = agregados_carbono()
    escribir_resumen(base, analisis, filas, meta, carbono)
    print('\nResultados en %s' % RESULTADOS)


if __name__ == '__main__':
    main()
