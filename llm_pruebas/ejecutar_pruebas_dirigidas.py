"""Pruebas DIRIGIDAS con un LLM: a Claude se le da la misma orden que a Rope.

Complementa a ejecutar_pruebas_llm.py (régimen autónomo: el modelo decide qué
refactorizar). Aquí el investigador decide qué refactorizar, igual que en
rope_pruebas/ejecutar_pruebas_rope.py: cada caso de este archivo corresponde a
un caso de la lista REFACTORIZACIONES de Rope, con el mismo id.

El MISMO archivo sirve para black_tesis y tornado_tesis (detecta el proyecto
por la estructura del repositorio). Cópialo, junto con prompt_v2.md, a
llm_pruebas/ de cada repositorio.

Flujo por llamada:
  1. Contexto = el paquete completo (src/black/*.py o tornado/*.py, igual que
     en el régimen autónomo, con caché de 1 h) + los archivos del proyecto
     (pruebas, .pyi, .json, .md...) que mencionan el nombre de la orden. Los
     elige este script por coincidencia textual: no revela qué archivos cambió
     Rope.
  2. Claude responde con bloques <edit> (buscar/reemplazar) y <riesgos>.
  3. Se aplican TODOS los bloques sobre una copia limpia. Si alguno no
     coincide exactamente una vez -> EDICIÓN INVÁLIDA (no se corren pruebas, no
     se reintenta ni se repara).
  4. Se corre la suite completa y se compara con la línea base (mismos
     veredictos que Rope; en Black, "solo formato" si el único fallo es
     test_piping y pasa tras formatear).
  5. Se cuentan las referencias que quedaron al nombre viejo (Rename).

El código original NUNCA se modifica. Cada ejecución se guarda en
llm_pruebas/resultados_dirigidas/<fecha_hora>/ y no se sobrescribe.

Uso (desde la raíz del repositorio, con ANTHROPIC_API_KEY exportada):
    .venv/bin/python llm_pruebas/ejecutar_pruebas_dirigidas.py --listar
    .venv/bin/python llm_pruebas/ejecutar_pruebas_dirigidas.py --fase 1 --dry-run
    .venv/bin/python llm_pruebas/ejecutar_pruebas_dirigidas.py --casos 02 --corridas 1   # humo
    caffeinate -dimsu .venv/bin/python -W ignore llm_pruebas/ejecutar_pruebas_dirigidas.py --fase 1
    .venv/bin/python llm_pruebas/ejecutar_pruebas_dirigidas.py --reanudar 20261124_093000 --fase 1
    .venv/bin/python llm_pruebas/ejecutar_pruebas_dirigidas.py --reevaluar 20261124_093000
    .venv/bin/python llm_pruebas/ejecutar_pruebas_dirigidas.py --probar-respuesta r.md --caso 02   # sin API
"""
import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

try:
    import anthropic
except ImportError:          # --listar, --dry-run y --probar-respuesta no lo necesitan
    anthropic = None

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parent
TRABAJO = AQUI / '_trabajo_dirigidas'
RESULTADOS = AQUI / 'resultados_dirigidas'
PROMPT = AQUI / 'prompt_v2.md'
PYTHON = sys.executable

# ---------------------------------------------------------------------------
# Proyecto (se detecta solo)
# ---------------------------------------------------------------------------

if (REPO / 'src' / 'black').is_dir():
    PROYECTO = 'black'
    PAQUETE = REPO / 'src' / 'black'
    BASE_ESPERADA = {'passed': 743, 'skipped': 2}
    IGNORAR_DIRS = {'.git', '.github', '.venv', '.pytest_cache', '.mypy_cache', '.tox',
                    '__pycache__', '.ropeproject', '.claude', 'rope_pruebas',
                    'llm_pruebas', 'huella_carbono', 'profiling'}
elif (REPO / 'tornado' / 'httputil.py').is_file():
    PROYECTO = 'tornado'
    PAQUETE = REPO / 'tornado'
    BASE_ESPERADA = {'passed': 1424, 'skipped': 111}
    IGNORAR_DIRS = {'.git', '.github', '.venv', '__pycache__', '.ropeproject', '.mypy_cache',
                    '.tox', 'build', 'rope_pruebas', 'llm_pruebas', 'docs', 'demos', 'maint'}
else:
    sys.exit('Ejecuta este script desde llm_pruebas/ de black_tesis o de tornado_tesis.')

IGNORAR = shutil.ignore_patterns(*IGNORAR_DIRS, '*.egg-info')
TEST_FORMATO = 'tests/test_black.py::BlackTestCase::test_piping'   # solo Black

# USD por millón de tokens:
#   (input, output, escritura de caché de 1 h, lectura de caché, escritura de caché de 5 min)
# Sonnet 5.5 cobra la lectura de caché a 0,10 (no 0,20 como Sonnet 5).
PRECIOS = {
    'claude-opus-5-5': (4.00, 20.00, 8.00, 0.20, 5.00),
    'claude-sonnet-5-5': (2.00, 10.00, 4.00, 0.10, 2.50),
    'claude-haiku-5-5': (0.10, 0.50, 0.20, 0.01, 0.125),
}

# Medición de carbono (opcional): si existe rope_pruebas/carbono_traza.py, cada
# llamada a la API y cada corrida de la suite se miden con CodeCarbon + una
# traza de potencia cada 0,1 s, igual que en los otros experimentos. Si no
# existe (p. ej. en otro repositorio), el script funciona igual sin medir.
MEDIDOR = None
MEDICIONES = []
try:
    sys.path.insert(0, str(REPO / 'rope_pruebas'))
    from carbono_traza import Medidor
except Exception:
    Medidor = None
CAMPOS_CARBONO = ('duracion_s', 'energia_kwh', 'energia_traza_kwh', 'emisiones_kg',
                  'emisiones_traza_kg', 'potencia_pico_w', 'potencia_media_traza_w',
                  'n_muestras')


def medir(fase, nombre, funcion, fila=None):
    """Ejecuta funcion() midiendo su carbono si hay medidor; anota el resultado en fila."""
    if MEDIDOR is None:
        return funcion()
    try:
        return MEDIDOR.medir(fase, nombre, funcion)
    finally:
        if fila is not None and MEDICIONES:
            fila.setdefault('carbono', {})[fase] = {c: MEDICIONES[-1][c] for c in CAMPOS_CARBONO}

EXTENSIONES = {'.py', '.pyi', '.json', '.toml', '.md', '.rst', '.txt', '.cfg', '.ini',
               '.yaml', '.yml'}
CARACTERES_POR_TOKEN = 2.6      # estimación (≈2,5-2,8 car./token); el costo real sale de la API
MAX_BYTES_ARCHIVO = 400_000

# ---------------------------------------------------------------------------
# Los casos (mismos ids que REFACTORIZACIONES de rope_pruebas)
# ---------------------------------------------------------------------------
# (id, operación, orden, términos, residuo)
#   términos: expresiones regulares; los archivos del proyecto (fuera del
#             paquete) que coinciden se añaden al contexto.
#   residuo:  expresión regular del nombre viejo; se cuentan las apariciones
#             que quedan tras la edición (solo Rename).

REF = ' Actualiza todas las referencias a ese nombre en el proyecto.'
REF_DOCS = (' Actualiza todas las referencias a ese nombre en el proyecto, incluidas las '
            'que aparezcan en strings y comentarios.')


def w(nombre):
    return r'\b%s\b' % re.escape(nombre)


CASOS_BLACK = [
    ('02_rename_funcion', 'Rename',
     'Renombra la función `lib2to3_parse`, definida en `src/black/parsing.py`, a `parse_to_tree`.' + REF,
     [w('lib2to3_parse')], w('lib2to3_parse')),
    ('03_rename_funcion_importada', 'Rename',
     'Renombra la función `parse_line_ranges`, definida en `src/black/ranges.py`, a `parse_line_range_specs`.' + REF,
     [w('parse_line_ranges')], w('parse_line_ranges')),
    ('04_rename_metodo', 'Rename',
     'Renombra el método `is_changed` de la clase `Cache`, definida en `src/black/cache.py`, a `has_changed`.' + REF,
     [w('is_changed')], w('is_changed')),
    ('05_rename_clase', 'Rename',
     'Renombra la clase `StringTransformer`, definida en `src/black/trans.py`, a `BaseStringTransformer`.' + REF,
     [w('StringTransformer')], w('StringTransformer')),
    ('06_rename_parametro', 'Rename',
     'Renombra el parámetro `fast` de la función `format_file_contents`, definida en `src/black/__init__.py`, '
     'a `skip_safety_checks`.' + REF,
     [w('format_file_contents')], None),
    ('06b_rename_parametro_posicional', 'Rename',
     'Renombra el parámetro `src_contents` de la función `format_file_contents`, definida en '
     '`src/black/__init__.py`, a `source`.' + REF,
     [w('format_file_contents')], None),
    ('07_extract_cache', 'Extract Method',
     'En la función `reformat_one` de `src/black/__init__.py`, extrae a una función nueva `_read_cache` el '
     'bloque que decide qué caché leer: empieza en la línea `if no_cache:` (con su cuerpo `cache = None`) y '
     'termina justo antes de la línea `if cache is not None:`. Sustituye el bloque por una llamada a la '
     'función nueva.', [], None),
    ('08_extract_stdin', 'Extract Method',
     'En la función `reformat_one` de `src/black/__init__.py`, extrae a una función nueva `_detect_stdin` el '
     'bloque `if str(src) == "-":` / `elif` / `else` que detecta si la entrada es stdin: empieza en la línea '
     '`if str(src) == "-":` y termina justo antes de la línea `if is_stdin:`. Sustituye el bloque por una '
     'llamada a la función nueva.', [], None),
    ('09_extract_con_continue', 'Extract Method',
     'En la función `get_sources` de `src/black/__init__.py`, dentro del bucle `for s in src:`, extrae a una '
     'función nueva `_resolve_stdin_source` el bloque que empieza en la línea `if s == "-" and stdin_filename:` '
     'y termina justo antes del comentario `# When the sources share no common parent`. Sustituye el bloque '
     'por una llamada a la función nueva.', [], None),
    ('10_extract_bucle', 'Extract Method',
     'En la función `get_sources` de `src/black/__init__.py`, extrae a una función nueva `_collect_sources` el '
     'bucle `for s in src:` completo: empieza en la línea `for s in src:` y termina justo antes de la línea '
     '`return sources`. Sustituye el bucle por una llamada a la función nueva.', [], None),
    ('10b_extract_bucle_sin_fstring', 'Extract Method',
     'En la función `diff` de `src/black/output.py`, extrae a una función nueva `_append_diff_lines` el bucle '
     '`for line in difflib.unified_diff(` completo: empieza en esa línea y termina justo antes de la línea '
     '`return "".join(diff_lines)`. Sustituye el bucle por una llamada a la función nueva.', [], None),
    ('11_inline_funcion', 'Inline',
     'Haz inline de la función `_splitlines_no_ff`, definida en `src/black/output.py`: sustituye cada llamada '
     'por el cuerpo de la función y elimina la definición.', [w('_splitlines_no_ff')], None),
    ('12_move_funcion', 'Move',
     'Mueve la función `re_compile_maybe_verbose` de `src/black/__init__.py` al módulo `src/black/files.py`. '
     'Actualiza las importaciones y los usos.', [w('re_compile_maybe_verbose')], None),
    ('13_rename_parcheada', 'Rename',
     'Renombra la función `dump_to_file`, definida en `src/black/output.py`, a `write_to_temp_file`.' + REF,
     [w('dump_to_file')], w('dump_to_file')),
    ('14_rename_parcheada_docs', 'Rename',
     'Renombra la función `dump_to_file`, definida en `src/black/output.py`, a `write_to_temp_file`.' + REF_DOCS,
     [w('dump_to_file')], w('dump_to_file')),
    ('15_rename_visitante', 'Rename',
     'Renombra el método `visit_suite` de la clase `LineGenerator`, definida en `src/black/linegen.py`, a '
     '`visit_block`.' + REF,
     [w('visit_suite')], w('visit_suite')),
    ('16_rename_preview', 'Rename',
     'Renombra el miembro `wrap_comprehension_in` del enum `Preview`, definido en `src/black/mode.py`, a '
     '`wrap_comprehension_in_clause`.' + REF,
     [w('wrap_comprehension_in')], w('wrap_comprehension_in')),
]

CASOS_TORNADO = [
    ('02_rename_funcion', 'Rename',
     'Renombra la función `url_concat`, definida en `tornado/httputil.py`, a `concat_url_args`.' + REF,
     [w('url_concat')], w('url_concat')),
    ('03_rename_funcion_importada', 'Rename',
     'Renombra la función `is_valid_ip`, definida en `tornado/netutil.py`, a `is_ip_address`.' + REF,
     [w('is_valid_ip')], w('is_valid_ip')),
    ('04_rename_metodo', 'Rename',
     'Renombra el método `_maybe_add_error_listener` de la clase `BaseIOStream`, definida en '
     '`tornado/iostream.py`, a `_ensure_error_listener`.' + REF,
     [w('_maybe_add_error_listener')], w('_maybe_add_error_listener')),
    ('05_rename_clase', 'Rename',
     'Renombra la clase `Configurable`, definida en `tornado/util.py`, a `ConfigurableBase`.' + REF,
     [w('Configurable')], w('Configurable')),
    ('06_rename_parametro', 'Rename',
     'Renombra el parámetro `plus` de la función `url_escape`, definida en `tornado/escape.py`, a `use_plus`.' + REF,
     [w('url_escape')], None),
    ('07_extract_boundary', 'Extract Method',
     'En la función `parse_multipart_form_data` de `tornado/httputil.py`, extrae a una función nueva '
     '`_unquote_boundary` el bloque que quita las comillas del boundary: empieza en la línea '
     '`if boundary.startswith(b\'"\') and boundary.endswith(b\'"\'):` y termina justo antes de la línea '
     '`final_boundary_index = data.rfind(`. Sustituye el bloque por una llamada a la función nueva.', [], None),
    ('08_extract_rango', 'Extract Method',
     'En la función `_parse_request_range` de `tornado/httputil.py`, extrae a una función nueva '
     '`_split_range_header` las líneas que separan la unidad y el valor: empiezan en '
     '`unit, _, value = range_header.partition("=")` y terminan justo antes de la línea `if unit != "bytes":`. '
     'Sustituye el bloque por una llamada a la función nueva.', [], None),
    ('09_extract_con_return', 'Extract Method',
     'En la función `_parse_request_range` de `tornado/httputil.py`, extrae a una función nueva '
     '`_parse_range_bounds` el bloque `try`/`except` que empieza en la línea `try:` que precede a '
     '`start = _int_or_none(start_b)` y termina justo antes de la línea `if end is not None:`. Sustituye el '
     'bloque por una llamada a la función nueva.', [], None),
    ('10_extract_bucle', 'Extract Method',
     'En la función `parse_body_arguments` de `tornado/httputil.py`, extrae a una función nueva '
     '`_merge_urlencoded_arguments` el bucle `for name, values in uri_arguments.items():` completo: termina '
     'justo antes de la línea `elif content_type.startswith("multipart/form-data"):`. Sustituye el bucle por '
     'una llamada a la función nueva.', [], None),
    ('11_inline_funcion', 'Inline',
     'Haz inline de la función `_int_or_none`, definida en `tornado/httputil.py`: sustituye cada llamada por '
     'el cuerpo de la función y elimina la definición.', [w('_int_or_none')], None),
    ('12_move_funcion', 'Move',
     'Mueve la función `_format_addr` de `tornado/tcpclient.py` al módulo `tornado/netutil.py`. Actualiza las '
     'importaciones y los usos.', [w('_format_addr')], None),
    ('13_rename_parcheada', 'Rename',
     'Renombra el método `_try_inline_read` de la clase `BaseIOStream`, definida en `tornado/iostream.py`, a '
     '`_read_inline_if_possible`.' + REF,
     [w('_try_inline_read')], w('_try_inline_read')),
    ('14_rename_con_doctest', 'Rename',
     'Renombra la función `_normalize_header`, definida en `tornado/httputil.py`, a `_to_header_case`.' + REF,
     [w('_normalize_header')], w('_normalize_header')),
    ('15_rename_con_doctest_docs', 'Rename',
     'Renombra la función `_normalize_header`, definida en `tornado/httputil.py`, a `_to_header_case`.' + REF_DOCS,
     [w('_normalize_header')], w('_normalize_header')),
    ('16_rename_en_test_modules', 'Rename',
     'Renombra la función `doctests`, definida en `tornado/httputil.py`, a `doctest_suite`.' + REF,
     [w('doctests')], r'httputil\.doctests|\bdef doctests\b'),
    ('17_rename_verbo_http', 'Rename',
     'Renombra el método `get` de la clase `HelloHandler`, definida en `tornado/test/web_test.py`, a '
     '`handle_get`.' + REF,
     [w('HelloHandler')], None),
    ('18_rename_handler_string', 'Rename',
     'Renombra la clase `HelloHandler`, definida en `tornado/test/web_test.py`, a `GreetingHandler`.' + REF,
     [w('HelloHandler')], w('HelloHandler')),
    ('19_rename_modulo', 'Rename (módulo)',
     'Renombra el módulo `tornado/locks.py` a `tornado/sync.py`. Actualiza todas las referencias al módulo en '
     'el proyecto.',
     [r'tornado\.locks', r'tornado/locks', r'from tornado import[^\n]*\blocks\b',
      r'\bimport locks\b', r'["\']locks["\']'],
     r'tornado\.locks|tornado/locks|from tornado import[^\n]*\blocks\b|\bimport locks\b'),
    ('20_extract_await', 'Extract Method',
     'En el método `_execute` de la clase `RequestHandler` (`tornado/web.py`), extrae a un método nuevo '
     '`_run_prepare` el bloque que llama a `self.prepare()` y espera su resultado: empieza en la línea '
     '`result = self.prepare()` y termina justo antes de la línea `if self._prepared_future is not None:`. '
     'Sustituye el bloque por una llamada al método nuevo.', [], None),
]


def construir_casos():
    lista = CASOS_BLACK if PROYECTO == 'black' else CASOS_TORNADO
    casos = []
    for cid, op, orden, terminos, residuo in lista:
        n = int(re.match(r'\d+', cid).group())
        fase = 3 if n >= 13 else (2 if op == 'Extract Method' else 1)
        casos.append({'id': cid, 'op': op, 'fase': fase, 'orden': orden,
                      'terminos': terminos, 'residuo': residuo})
    return casos


CASOS = construir_casos()


def seleccionar(args):
    if args.casos:
        elegidos = []
        for c in args.casos:
            hallados = [k for k in CASOS if k['id'] == c or k['id'].split('_')[0] == c]
            if not hallados:
                sys.exit('Caso desconocido: %s (usa --listar)' % c)
            elegidos += hallados
        return elegidos
    if args.fase:
        return [k for k in CASOS if k['fase'] in args.fase]
    if args.todos:
        return list(CASOS)
    sys.exit('Indica qué correr: --fase N, --casos ID... o --todos (usa --listar para verlos).')


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def copia_limpia(nombre):
    destino = TRABAJO / nombre
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(REPO, destino, ignore=IGNORAR)
    return destino


def correr_pytest(carpeta):
    """Black: pytest sobre la copia. Devuelve (resumen, salida)."""
    env = dict(os.environ, PYTHONPATH=str(carpeta / 'src'))
    proc = subprocess.run(
        [PYTHON, '-m', 'pytest', 'tests', '-q', '-rsfE', '-p', 'no:cacheprovider'],
        cwd=carpeta, capture_output=True, text=True, env=env)
    salida = proc.stdout + proc.stderr
    finales = [l for l in salida.splitlines()
               if re.search(r'\d+ (passed|failed|errors?)\b.* in [\d.]+s', l)]
    final = finales[-1] if finales else ''
    resumen = {'returncode': proc.returncode}
    for clave in ('passed', 'failed', 'skipped', 'error', 'errors'):
        m = re.search(r'(\d+) ' + clave + r'\b', final)
        resumen[clave] = int(m.group(1)) if m else 0
    resumen['errors'] += resumen.pop('error')
    resumen['fallidos'] = sorted(set(re.findall(r'^(?:FAILED|ERROR) (\S+?)(?: - |$)', salida, re.M)))
    return resumen, salida


def correr_tests_tornado(carpeta):
    """Tornado: suite oficial (unittest). Devuelve (resumen, salida)."""
    env = dict(os.environ, PYTHONPATH=str(carpeta))
    proc = subprocess.run([PYTHON, '-m', 'tornado.test.runtests'],
                          cwd=carpeta, capture_output=True, text=True, env=env)
    salida = proc.stdout + proc.stderr
    resumen = {'returncode': proc.returncode}
    m = re.search(r'^Ran (\d+) tests? in', salida, re.M)
    ejecutados = int(m.group(1)) if m else 0
    for clave, patron in (('failed', 'failures'), ('errors', 'errors'),
                          ('skipped', 'skipped'), ('expected_failures', 'expected failures')):
        m2 = re.search(r'^(?:OK|FAILED) \(.*\b' + patron + r'=(\d+)', salida, re.M)
        resumen[clave] = int(m2.group(1)) if m2 else 0
    if not m:
        resumen['errors'] = max(resumen['errors'], 1)
    resumen['ran'] = ejecutados
    resumen['passed'] = max(ejecutados - resumen['failed'] - resumen['errors']
                            - resumen['skipped'] - resumen['expected_failures'], 0)
    resumen['fallidos'] = sorted(set(re.findall(r'^(?:FAIL|ERROR): (.+)$', salida, re.M)))
    return resumen, salida


def correr_suite(carpeta):
    return correr_pytest(carpeta) if PROYECTO == 'black' else correr_tests_tornado(carpeta)


def verificar_tornado_no_instalado():
    import importlib.metadata
    try:
        importlib.metadata.distribution('tornado')
    except importlib.metadata.PackageNotFoundError:
        return
    sys.exit('tornado está instalado en %s; desinstálalo (pip uninstall tornado) para que los '
             'tests usen solo la copia.' % sys.prefix)


# ---------------------------------------------------------------------------
# Contexto
# ---------------------------------------------------------------------------

def contexto_paquete():
    """Mismo prefijo que el régimen autónomo: todos los módulos del paquete."""
    partes = []
    for ruta in sorted(PAQUETE.glob('*.py')):
        rel = ruta.relative_to(REPO).as_posix()
        partes.append('<archivo ruta="%s">\n%s\n</archivo>' % (rel, ruta.read_text()))
    return 'Código actual del paquete %s:\n\n' % PROYECTO + '\n\n'.join(partes)


_ARCHIVOS = None


def archivos_proyecto():
    """{ruta relativa: texto} de los archivos de texto del proyecto (fuera del paquete)."""
    global _ARCHIVOS
    if _ARCHIVOS is None:
        en_prefijo = {p.relative_to(REPO).as_posix() for p in PAQUETE.glob('*.py')}
        _ARCHIVOS = {}
        for raiz, dirs, nombres in os.walk(REPO):
            dirs[:] = [d for d in dirs if d not in IGNORAR_DIRS and not d.endswith('.egg-info')
                       and d not in ('_trabajo_dirigidas', '_trabajo', 'resultados',
                                     'resultados_dirigidas')]
            for n in nombres:
                p = Path(raiz) / n
                rel = p.relative_to(REPO).as_posix()
                if p.suffix not in EXTENSIONES or rel in en_prefijo:
                    continue
                if p.stat().st_size > MAX_BYTES_ARCHIVO:
                    continue
                try:
                    _ARCHIVOS[rel] = p.read_text()
                except UnicodeDecodeError:
                    pass
    return _ARCHIVOS


def contexto_extra(caso, max_tokens):
    """Archivos que mencionan el nombre, ordenados por nº de coincidencias.

    Devuelve (texto, incluidos, omitidos). Un archivo que no cabe en el
    presupuesto se omite entero (no se recorta: las ediciones necesitan el
    texto exacto).
    """
    if not caso['terminos']:
        return '', [], []
    patrones = [re.compile(t) for t in caso['terminos']]
    hallados = []
    for rel, texto in archivos_proyecto().items():
        n = sum(len(p.findall(texto)) for p in patrones)
        if n:
            hallados.append((n, rel, texto))
    hallados.sort(key=lambda x: (-x[0], x[1]))
    presupuesto = max_tokens * CARACTERES_POR_TOKEN
    usados, partes, incluidos, omitidos = 0, [], [], []
    for n, rel, texto in hallados:
        if usados + len(texto) > presupuesto:
            omitidos.append({'archivo': rel, 'coincidencias': n, 'caracteres': len(texto)})
            continue
        usados += len(texto)
        partes.append('<archivo ruta="%s">\n%s\n</archivo>' % (rel, texto))
        incluidos.append({'archivo': rel, 'coincidencias': n, 'caracteres': len(texto)})
    if not partes:
        return '', incluidos, omitidos
    cabecera = ('Otros archivos del proyecto que mencionan el nombre de la orden (no forman parte '
                'del paquete anterior):\n\n')
    return cabecera + '\n\n'.join(partes), incluidos, omitidos


# ---------------------------------------------------------------------------
# Respuesta del modelo -> ediciones
# ---------------------------------------------------------------------------

RE_EDIT = re.compile(r'<edit\s+file="([^"]+)"\s*>\s*<search>\n?(.*?)\n?</search>\s*'
                     r'<replace>\n?(.*?)\n?</replace>\s*</edit>', re.S)
RE_RENAME = re.compile(r'<rename_file\s+from="([^"]+)"\s+to="([^"]+)"\s*/>')
RE_RIESGOS = re.compile(r'<riesgos>(.*?)</riesgos>', re.S)


def leer(p):
    return p.read_bytes().decode('utf-8')


def escribir(p, texto):
    p.write_bytes(texto.encode('utf-8'))


def aplicar_respuesta(texto, carpeta):
    """Aplica los <edit> y <rename_file> de `texto` sobre `carpeta`.

    Todo o nada en cuanto a validez: devuelve (tocados, errores). Si hay
    errores, el llamador no corre las pruebas.
    """
    ediciones = RE_EDIT.findall(texto)
    renombres = RE_RENAME.findall(texto)
    errores, tocados = [], []
    raiz = carpeta.resolve()
    for ruta, busca, nuevo in ediciones:
        p = (carpeta / ruta).resolve()
        if not str(p).startswith(str(raiz) + os.sep) or not p.is_file():
            errores.append('archivo inexistente o fuera del proyecto: %s' % ruta)
            continue
        if not busca.strip():
            errores.append('bloque <search> vacío en %s' % ruta)
            continue
        actual = leer(p)
        n = actual.count(busca)
        if n != 1:
            errores.append('%s: el texto buscado aparece %d veces (debe ser 1): %r'
                           % (ruta, n, busca[:80]))
            continue
        escribir(p, actual.replace(busca, nuevo, 1))
        if ruta not in tocados:
            tocados.append(ruta)
    if not errores:
        for origen, destino in renombres:
            a, b = carpeta / origen, carpeta / destino
            if not a.is_file() or b.exists():
                errores.append('renombrado inválido: %s -> %s' % (origen, destino))
                continue
            b.parent.mkdir(parents=True, exist_ok=True)
            a.rename(b)
            tocados.append('%s -> %s' % (origen, destino))
    return tocados, errores, len(ediciones), len(renombres)


def diff_de(tocados, carpeta):
    trozos = []
    for t in tocados:
        if ' -> ' in t:
            origen, destino = t.split(' -> ')
            nuevo = leer(carpeta / destino) if (carpeta / destino).is_file() else ''
            trozos.append(''.join(difflib.unified_diff(
                leer(REPO / origen).splitlines(True), nuevo.splitlines(True),
                'a/' + origen, 'b/' + destino)))
            continue
        existe = (carpeta / t).is_file()
        if existe:
            trozos.append(''.join(difflib.unified_diff(
                leer(REPO / t).splitlines(True), leer(carpeta / t).splitlines(True),
                'a/' + t, 'b/' + t)))
    return ''.join(trozos)


def contar_residuos(caso, carpeta):
    """Apariciones del nombre viejo que quedan en la copia (código vs. texto)."""
    if not caso['residuo']:
        return None
    rx = re.compile(caso['residuo'])
    codigo, texto = {}, {}
    for raiz, dirs, nombres in os.walk(carpeta):
        dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git')]
        for n in nombres:
            p = Path(raiz) / n
            if p.suffix not in EXTENSIONES:
                continue
            try:
                k = len(rx.findall(leer(p)))
            except UnicodeDecodeError:
                continue
            if k:
                destino = codigo if p.suffix in ('.py', '.pyi', '.json') else texto
                destino[p.relative_to(carpeta).as_posix()] = k
    return {'codigo': sum(codigo.values()), 'archivos_codigo': codigo,
            'texto': sum(texto.values()), 'archivos_texto': texto}


# ---------------------------------------------------------------------------
# Llamada a la API
# ---------------------------------------------------------------------------

def costo(modelo, uso):
    precios = PRECIOS.get(modelo)
    if not precios:
        return None
    p_in, p_out, p_cw, p_cr, p_cw5 = precios
    # Si la API no desglosa la escritura por TTL, se cobra todo como 1 h (cota superior).
    w5 = uso.get('cache_write_5m', 0)
    w1 = uso.get('cache_write_1h', uso['cache_write'] - w5)
    return round((uso['input'] * p_in + uso['output'] * p_out
                  + w1 * p_cw + w5 * p_cw5 + uso['cache_read'] * p_cr) / 1e6, 4)


def es_error_de_red(e):
    return (isinstance(e, (anthropic.APIConnectionError, OSError))
            or type(e).__module__.split('.')[0].startswith('httpx'))


def pedir(cliente, args, sistema, prefijo, extra, orden):
    t0 = time.perf_counter()
    contenido = [
        # Prefijo idéntico en todas las llamadas -> se reutiliza la caché (TTL 1 h).
        {'type': 'text', 'text': prefijo, 'cache_control': {'type': 'ephemeral', 'ttl': '1h'}},
        # Bloque del caso (archivos extra + orden): es idéntico en las corridas de un
        # mismo caso, que van seguidas -> caché de 5 min. Solo cambia el precio, no el
        # texto que recibe el modelo: la corrida 1 lo escribe y las demás lo leen.
        {'type': 'text', 'text': (extra + '\n\n' if extra else '') + 'Orden de refactoring:\n' + orden,
         'cache_control': {'type': 'ephemeral', 'ttl': '5m'}},
    ]
    with cliente.beta.messages.stream(
        model=args.modelo,
        max_tokens=64000,
        system=sistema,
        output_config={'effort': args.effort},
        betas=['server-side-fallback-2026-07-01'],
        fallbacks='default',
        messages=[{'role': 'user', 'content': contenido}],
    ) as stream:
        for _ in stream:
            pass
        respuesta = stream.get_final_message()
    texto = ''.join(b.text for b in respuesta.content if b.type == 'text')
    u = respuesta.usage
    uso = {'input': u.input_tokens, 'output': u.output_tokens,
           'cache_write': u.cache_creation_input_tokens or 0,
           'cache_read': u.cache_read_input_tokens or 0}
    desglose = getattr(u, 'cache_creation', None)
    if desglose is not None:
        uso['cache_write_1h'] = getattr(desglose, 'ephemeral_1h_input_tokens', 0) or 0
        uso['cache_write_5m'] = getattr(desglose, 'ephemeral_5m_input_tokens', 0) or 0
    meta = {'modelo_respuesta': respuesta.model, 'stop_reason': respuesta.stop_reason,
            'message_id': respuesta.id, 'tiempo_llm_s': round(time.perf_counter() - t0, 1),
            'tokens': uso, 'costo_usd': costo(respuesta.model, uso)}
    return texto, meta


def pedir_con_reintentos(cliente, args, sistema, prefijo, extra, orden, intentos=4):
    """Reintenta SOLO ante errores de red (no es un reintento de la tarea)."""
    for intento in range(1, intentos + 1):
        try:
            texto, meta = pedir(cliente, args, sistema, prefijo, extra, orden)
            meta['intentos_red'] = intento
            return texto, meta
        except Exception as e:
            if not es_error_de_red(e) or intento == intentos:
                raise
            espera = 30 * intento
            print('  error de red (%s), reintento %d en %ds' % (type(e).__name__, intento, espera))
            time.sleep(espera)


# ---------------------------------------------------------------------------
# Una corrida
# ---------------------------------------------------------------------------

def formatear_y_probar(carpeta, tocados):
    """Black: formatea los .py de src/black tocados (config de test_piping) y repite la suite."""
    destino = TRABAJO / (carpeta.name + '_formateado')
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(carpeta, destino)
    archivos = [t.split(' -> ')[-1] for t in tocados if t.split(' -> ')[-1].startswith('src/black/')
                and t.endswith('.py')]
    if archivos:
        subprocess.run([PYTHON, '-m', 'black', '-q', '--config', 'tests/empty.toml'] + archivos,
                       cwd=destino, check=True)
    resumen, salida = correr_suite(destino)
    shutil.rmtree(destino, ignore_errors=True)
    return resumen, salida


def evaluar(fila, texto, caso, base, salida_dir, conservar=False):
    """Aplica la respuesta a una copia limpia, corre la suite y fija el veredicto."""
    nombre = fila['id']
    riesgos = RE_RIESGOS.findall(texto)
    fila['riesgos_declarados'] = riesgos[-1].strip() if riesgos else ''
    fila['aviso_riesgo'] = bool(fila['riesgos_declarados']) and \
        fila['riesgos_declarados'].lower().strip(' .`') != 'ninguno'
    if fila.get('stop_reason') == 'refusal':
        fila['veredicto'] = 'RECHAZADA POR EL MODELO'
        return fila
    carpeta = copia_limpia(nombre)
    tocados, errores, n_edit, n_ren = aplicar_respuesta(texto, carpeta)
    fila['bloques_edit'], fila['bloques_rename'] = n_edit, n_ren
    if errores:
        fila['veredicto'] = 'EDICIÓN INVÁLIDA'
        fila['errores_edicion'] = errores
        shutil.rmtree(carpeta, ignore_errors=True)
        return fila
    if not tocados:
        fila['veredicto'] = 'SIN EDICIONES'
        shutil.rmtree(carpeta, ignore_errors=True)
        return fila
    diff = diff_de(tocados, carpeta)
    (salida_dir / (nombre + '.diff')).write_text(diff)
    fila['archivos_modificados'] = tocados
    fila['lineas_agregadas'] = sum(1 for l in diff.splitlines() if l.startswith('+') and not l.startswith('+++'))
    fila['lineas_eliminadas'] = sum(1 for l in diff.splitlines() if l.startswith('-') and not l.startswith('---'))
    fila['residuos'] = contar_residuos(caso, carpeta)

    resumen, salida = medir('tests', nombre, lambda: correr_suite(carpeta), fila)
    (salida_dir / (nombre + '_pytest.txt')).write_text(salida)
    fila['tests'] = resumen
    igual = (resumen['passed'] == base['passed'] and resumen['failed'] == 0
             and resumen['errors'] == 0)
    if igual:
        fila['veredicto'] = 'COMPORTAMIENTO PRESERVADO'
    elif (PROYECTO == 'black' and resumen['fallidos'] == [TEST_FORMATO] and resumen['errors'] == 0):
        tras, salida_black = formatear_y_probar(carpeta, tocados)
        (salida_dir / (nombre + '_formateado_pytest.txt')).write_text(salida_black)
        fila['tests_tras_black'] = tras
        ok = tras['passed'] == base['passed'] and tras['failed'] == 0 and tras['errors'] == 0
        fila['veredicto'] = 'ROMPE TESTS (solo formato)' if ok else 'ROMPE TESTS'
    else:
        fila['veredicto'] = 'ROMPE TESTS'
    if fila.get('stop_reason') == 'max_tokens':
        fila['veredicto'] += ' (respuesta truncada)'
    if not conservar:
        shutil.rmtree(carpeta, ignore_errors=True)
    return fila


def imprimir(fila):
    t = fila.get('tests') or {}
    print('[%s] %s  pasan=%s fallan=%s  $%s  %ss%s' % (
        fila['id'], fila['veredicto'], t.get('passed', '-'), t.get('failed', '-'),
        fila.get('costo_usd'), fila.get('tiempo_llm_s'),
        '  residuos=%s' % fila['residuos']['codigo'] if fila.get('residuos') else ''))
    for e in fila.get('errores_edicion', [])[:3]:
        print('    ! %s' % e)


def corrida(cliente, args, sistema, prefijo, caso, n, base, salida_dir):
    nombre = '%s_run%d' % (caso['id'], n)
    fila = {'id': nombre, 'caso': caso['id'], 'operacion': caso['op'], 'fase': caso['fase'],
            'corrida': n}
    extra, incluidos, omitidos = contexto_extra(caso, args.max_tokens_extra)
    fila['contexto_extra'] = {'incluidos': incluidos, 'omitidos': omitidos}
    try:
        texto, meta = medir('llm', nombre, lambda: pedir_con_reintentos(
            cliente, args, sistema, prefijo, extra, caso['orden']), fila)
    except anthropic.APIStatusError as e:
        fila['veredicto'] = 'ERROR API %s' % e.status_code
        fila['detalle'] = str(e.message)
        print('[%s] %s' % (nombre, fila['veredicto']))
        return fila
    fila.update(meta)
    (salida_dir / (nombre + '_respuesta.md')).write_text(texto)
    evaluar(fila, texto, caso, base, salida_dir)
    imprimir(fila)
    if MEDIDOR is not None:
        MEDIDOR.guardar_traza(salida_dir / 'traza_carbono.csv', anexar=True)
    return fila


# ---------------------------------------------------------------------------
# Reporte
# ---------------------------------------------------------------------------

def escribir_resumen(args, sistema, base, filas, salida_dir):
    total = round(sum(f.get('costo_usd') or 0 for f in filas), 4)
    L = ['# Pruebas dirigidas con un LLM (%s)' % PROYECTO, '',
         '- Python: `%s`' % sys.version.split()[0],
         '- SDK anthropic: `%s`' % (anthropic.__version__ if anthropic else 'n/d'),
         '- Modelo solicitado: `%s` (effort `%s`)' % (args.modelo, args.effort),
         '- Prompt: `prompt_v2.md` (SHA-256 `%s`)' % hashlib.sha256(sistema.encode()).hexdigest(),
         '- Fecha: %s' % time.strftime('%Y-%m-%d %H:%M'),
         '- Costo total: US$ %.4f' % total, '',
         '## Línea base', '',
         '%s passed, %s failed, %s skipped, %s errors' % (
             base['passed'], base['failed'], base['skipped'], base['errors']), '',
         '## Corridas', '',
         '| Corrida | Operación | Veredicto | Pasan/Fallan | Archivos | +/− | Residuos (código/texto) | Avisó riesgo | Costo | Tiempo (s) |',
         '|---|---|---|---|---|---|---|---|---|---|']
    for f in filas:
        t = f.get('tests') or {}
        r = f.get('residuos')
        L.append('| %s | %s | **%s** | %s/%s | %d | +%s/−%s | %s | %s | %s | %s |' % (
            f['id'], f.get('operacion', ''), f['veredicto'], t.get('passed', '-'), t.get('failed', '-'),
            len(f.get('archivos_modificados', [])), f.get('lineas_agregadas', '-'),
            f.get('lineas_eliminadas', '-'),
            '%d/%d' % (r['codigo'], r['texto']) if r else '-',
            'sí' if f.get('aviso_riesgo') else 'no', f.get('costo_usd', '-'), f.get('tiempo_llm_s', '-')))
    L += ['', '## Por caso', '', '| Caso | Corridas | Preservan | Solo formato | Rompen | Inválidas | Otras |',
          '|---|---|---|---|---|---|---|']
    for cid in dict.fromkeys(f['caso'] for f in filas):
        fs = [f for f in filas if f['caso'] == cid]
        pres = sum(f['veredicto'] == 'COMPORTAMIENTO PRESERVADO' for f in fs)
        form = sum(f['veredicto'].startswith('ROMPE TESTS (solo formato)') for f in fs)
        rom = sum(f['veredicto'].startswith('ROMPE TESTS') for f in fs) - form
        inv = sum(f['veredicto'] == 'EDICIÓN INVÁLIDA' for f in fs)
        L.append('| %s | %d | %d | %d | %d | %d | %d |' % (cid, len(fs), pres, form, rom, inv,
                                                         len(fs) - pres - form - rom - inv))
    (salida_dir / 'resumen.md').write_text('\n'.join(L) + '\n')
    (salida_dir / 'resumen.json').write_text(json.dumps(
        {'proyecto': PROYECTO, 'python': sys.version.split()[0],
         'anthropic': anthropic.__version__ if anthropic else None,
         'modelo': args.modelo, 'effort': args.effort, 'prompt': sistema,
         'prompt_sha256': hashlib.sha256(sistema.encode()).hexdigest(),
         'linea_base': base, 'costo_total_usd': total, 'corridas': filas},
        indent=2, ensure_ascii=False))


def listar(casos):
    print('Proyecto: %s  (%d casos)\n' % (PROYECTO, len(CASOS)))
    for c in casos:
        print('fase %d | %-32s | %-15s | %s' % (c['fase'], c['id'], c['op'], c['orden'][:110]))


def dry_run(args, casos, sistema):
    prefijo = contexto_paquete()
    n_pref = len(prefijo) / CARACTERES_POR_TOKEN
    print('=== SYSTEM (prompt_v2.md, SHA-256 %s) ===\n%s\n' % (
        hashlib.sha256(sistema.encode()).hexdigest(), sistema))
    print('Prefijo (paquete completo): %d caracteres, ≈ %d tokens\n' % (len(prefijo), n_pref))
    p_in, p_out, p_cw, p_cr, p_cw5 = PRECIOS[args.modelo]
    total = n_pref * p_cw / 1e6            # una escritura de la caché de 1 h (fases seguidas)
    for c in casos:
        extra, inc, omi = contexto_extra(c, args.max_tokens_extra)
        n_extra = len(extra) / CARACTERES_POR_TOKEN
        # corrida 1: escribe el bloque del caso (5 min); las demás lo leen
        por_llamada = (n_extra * p_cw5 + n_pref * p_cr + 4000 * p_out) / 1e6
        siguientes = (n_extra * p_cr + n_pref * p_cr + 4000 * p_out) / 1e6
        total += por_llamada + siguientes * (args.corridas - 1)
        print('%s  [%s, fase %d]  extra≈%d tokens (%d archivos%s)  ≈US$%.3f/llamada' % (
            c['id'], c['op'], c['fase'], n_extra, len(inc),
            ', %d OMITIDOS' % len(omi) if omi else '', por_llamada))
        print('    ORDEN: %s' % c['orden'])
        for i in inc[:8]:
            print('    + %s (%d coincidencias, %d car.)' % (i['archivo'], i['coincidencias'], i['caracteres']))
        if len(inc) > 8:
            print('    + ... y %d archivos más' % (len(inc) - 8))
        for o in omi:
            print('    - OMITIDO por presupuesto: %s (%d car.)' % (o['archivo'], o['caracteres']))
    print('\n%d casos × %d corridas = %d llamadas. Costo estimado ≈ US$ %.2f '
          '(supone 4.000 tokens de salida y la caché reutilizada; confírmalo con la prueba de humo).'
          % (len(casos), args.corridas, len(casos) * args.corridas, total))


def linea_base(salida_dir, abortar=True):
    carpeta = copia_limpia('00_linea_base')
    print('[linea base] corriendo la suite original (puede tardar)...')
    base, salida = correr_suite(carpeta)
    shutil.rmtree(carpeta, ignore_errors=True)
    (salida_dir / '00_linea_base_pytest.txt').write_text(salida)
    base.setdefault('skipped', 0)
    print('[linea base] %s' % {k: v for k, v in base.items() if k != 'fallidos'})
    mal = (base['failed'] or base['errors']
           or any(base.get(k) != v for k, v in BASE_ESPERADA.items()))
    if mal:
        msg = ('La línea base no coincide con la esperada %s: salió %s (ver %s). Revisa el entorno '
               '(venv, dependencias, tornado desinstalado) antes de gastar API.'
               % (BASE_ESPERADA, {k: base.get(k) for k in list(BASE_ESPERADA) + ['failed', 'errors']},
                  salida_dir / '00_linea_base_pytest.txt'))
        if abortar:
            sys.exit(msg)
        print('  AVISO: ' + msg)
    return base


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--modelo', default='claude-sonnet-5-5')
    ap.add_argument('--effort', default='high', choices=['low', 'medium', 'high', 'xhigh', 'max'])
    ap.add_argument('--corridas', type=int, default=3)
    ap.add_argument('--fase', type=int, nargs='+', choices=[1, 2, 3],
                    help='1: Rename/Inline/Move · 2: Extract · 3: casos propios (13+)')
    ap.add_argument('--casos', nargs='+', metavar='ID', help='p. ej. 02 06b 12 (o el id completo)')
    ap.add_argument('--todos', action='store_true')
    ap.add_argument('--listar', action='store_true')
    ap.add_argument('--dry-run', action='store_true',
                    help='muestra órdenes, contexto y costo estimado sin llamar a la API')
    ap.add_argument('--max-tokens-extra', type=int, default=250_000,
                    help='tope (estimado) de tokens de archivos adicionales por llamada')
    ap.add_argument('--tope-usd', type=float, default=25.0,
                    help='se detiene al superar este gasto en la ejecución (reanudable)')
    ap.add_argument('--reanudar', metavar='CARPETA')
    ap.add_argument('--reevaluar', metavar='CARPETA',
                    help='vuelve a aplicar y probar respuestas ya guardadas, sin llamar a la API')
    ap.add_argument('--probar-respuesta', metavar='ARCHIVO',
                    help='evalúa una respuesta escrita a mano (sin API); requiere --caso')
    ap.add_argument('--conservar', action='store_true', help='no borrar las copias de trabajo')
    args = ap.parse_args()

    sistema = PROMPT.read_text()
    if args.listar:
        listar(seleccionar(args) if (args.casos or args.fase or args.todos) else CASOS)
        return
    if args.dry_run:
        dry_run(args, seleccionar(args), sistema)
        return
    if PROYECTO == 'tornado':
        verificar_tornado_no_instalado()

    if args.probar_respuesta:
        caso = seleccionar(args)[0]
        salida_dir = RESULTADOS / ('prueba_' + time.strftime('%Y%m%d_%H%M%S'))
        salida_dir.mkdir(parents=True)
        base = linea_base(salida_dir, abortar=False)
        fila = {'id': caso['id'] + '_manual', 'caso': caso['id'], 'operacion': caso['op'],
                'fase': caso['fase'], 'corrida': 0}
        evaluar(fila, Path(args.probar_respuesta).read_text(), caso, base, salida_dir, args.conservar)
        imprimir(fila)
        escribir_resumen(args, sistema, base, [fila], salida_dir)
        print('\nResultados en %s' % salida_dir)
        return

    if args.reevaluar:
        salida_dir = RESULTADOS / args.reevaluar
        previo = json.loads((salida_dir / 'resumen.json').read_text())
        base = previo['linea_base']
        por_id = {c['id']: c for c in CASOS}
        filas = previo['corridas']
        for i, f in enumerate(filas):
            r = salida_dir / (f['id'] + '_respuesta.md')
            if not r.exists():
                continue
            for k in ('tests', 'tests_tras_black', 'errores_edicion', 'residuos',
                      'archivos_modificados'):
                f.pop(k, None)
            anterior = f.get('veredicto')
            filas[i] = evaluar(f, r.read_text(), por_id[f['caso']], base, salida_dir)
            filas[i]['reevaluacion'] = {'fecha': time.strftime('%Y-%m-%d %H:%M'),
                                        'veredicto_anterior': anterior}
            imprimir(filas[i])
        args.modelo, args.effort = previo['modelo'], previo['effort']
        escribir_resumen(args, previo['prompt'], base, filas, salida_dir)
        return

    casos = seleccionar(args)
    if anthropic is None:
        sys.exit('Falta el paquete anthropic: .venv/bin/pip install anthropic')
    cliente = anthropic.Anthropic()
    prefijo = contexto_paquete()
    global MEDIDOR
    if Medidor is not None:
        MEDIDOR = Medidor(os.environ.get('CODECARBON_PAIS', 'COL'),
                          float(os.environ.get('CODECARBON_TDP', '20')), MEDICIONES,
                          '%s_llm_dirigidas' % PROYECTO)
    filas = []
    if args.reanudar:
        salida_dir = RESULTADOS / args.reanudar
        previo = json.loads((salida_dir / 'resumen.json').read_text())
        assert previo['prompt'] == sistema, 'prompt_v2.md cambió desde la ejecución original'
        assert (previo['modelo'], previo['effort']) == (args.modelo, args.effort)
        filas = [f for f in previo['corridas'] if not f['veredicto'].startswith('ERROR')]
        base = previo['linea_base']
        print('[reanudar] %d corridas ya hechas en %s' % (len(filas), salida_dir))
    else:
        salida_dir = RESULTADOS / time.strftime('%Y%m%d_%H%M%S')
        salida_dir.mkdir(parents=True)
        (salida_dir / 'prompt.md').write_text(sistema)
        base = linea_base(salida_dir)
    print('Prompt SHA-256: %s' % hashlib.sha256(sistema.encode()).hexdigest())
    hechas = {f['id'] for f in filas}

    for caso in casos:
        for n in range(1, args.corridas + 1):
            if '%s_run%d' % (caso['id'], n) in hechas:
                continue
            gastado = sum(f.get('costo_usd') or 0 for f in filas)
            if gastado > args.tope_usd:
                print('\nTope de US$ %.2f superado (%.2f). Reanuda con --reanudar %s'
                      % (args.tope_usd, gastado, salida_dir.name))
                escribir_resumen(args, sistema, base, filas, salida_dir)
                return
            filas.append(corrida(cliente, args, sistema, prefijo, caso, n, base, salida_dir))
            escribir_resumen(args, sistema, base, filas, salida_dir)
    print('\nResultados en %s' % salida_dir)


if __name__ == '__main__':
    main()
