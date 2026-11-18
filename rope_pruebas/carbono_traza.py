"""Medición de carbono DURANTE la ejecución (traza de potencia en el tiempo).

Problema que resuelve
---------------------
Dentro de una *task* de CodeCarbon (start_task/stop_task) la energía se calcula
UNA sola vez, al llamar a stop_task: usa la carga media de CPU registrada por un
monitor que muestrea cada 1 s. Resultado: se obtiene el total "después de la
ejecución", pero no se ve qué pasó durante ella, y una operación de menos de 1 s
(como una refactorización de Rope) casi no deja muestras.

Qué hace este módulo
--------------------
`Medidor` envuelve un OfflineEmissionsTracker y, mientras corre cada fase
(Rope, suite de tests, llamada al LLM...), lanza un hilo muestreador que cada
`INTERVALO_S` segundos (0,1 s por defecto) lee la carga de CPU de TODO el equipo
y calcula la potencia instantánea con el mismo modelo que CodeCarbon usa en
macOS sin sudo:

    P_cpu = TDP * (0.1 + 0.9 * carga^3)        (carga entre 0 y 1)
    P_ram = constante de CodeCarbon (3 W en este equipo)

La energía de la fase es la integral (regla del rectángulo) de esas muestras.
Cada muestra se guarda en `traza_carbono.csv` con: fase, tiempo transcurrido,
carga, potencia, energía acumulada y emisiones acumuladas. Así se puede graficar
la curva de consumo de cada operación y ver los picos.

Validación cruzada: de cada fase se guardan los dos valores, el de CodeCarbon
(`energia_kwh`, total al final) y el integrado de la traza
(`energia_traza_kwh`). Deben ser parecidos; la diferencia es el error del
muestreo de 1 s de CodeCarbon frente al de 0,1 s de la traza.

En la fase del LLM (llamada a la API) lo único medible es el consumo LOCAL: el
equipo esperando la respuesta por red. La energía de los servidores de Anthropic
no se puede medir desde aquí; por eso se guardan también los tokens.
"""
import logging
import threading
import time

import psutil
from codecarbon import OfflineEmissionsTracker

INTERVALO_S = 0.1


class _Muestreador(threading.Thread):
    """Hilo que anota (t, carga, potencia) cada INTERVALO_S segundos."""

    def __init__(self, tdp_w, ram_w, intervalo):
        super().__init__(daemon=True)
        self.tdp_w, self.ram_w, self.intervalo = tdp_w, ram_w, intervalo
        self.muestras = []          # (t_s, carga_pct, p_cpu_w, p_ram_w, dt_s)
        self._parar = threading.Event()

    def run(self):
        psutil.cpu_percent(None)    # la 1.ª lectura siempre da 0; se descarta
        t0 = anterior = time.perf_counter()
        while not self._parar.wait(self.intervalo):
            ahora = time.perf_counter()
            carga = psutil.cpu_percent(None)
            p_cpu = self.tdp_w * (0.1 + 0.9 * (carga / 100.0) ** 3)
            self.muestras.append((ahora - t0, carga, p_cpu, self.ram_w,
                                  ahora - anterior))
            anterior = ahora

    def parar(self):
        self._parar.set()
        self.join()


class Medidor:
    """Tracker de CodeCarbon + traza de potencia durante cada fase.

    `mediciones` es la lista (compartida con el script que lo usa) donde se
    acumula una fila por fase; `traza` es la lista de muestras individuales.
    Cualquier otro atributo (p. ej. `_hardware`) se delega al tracker.
    """

    def __init__(self, pais, tdp_cpu_w, mediciones, proyecto):
        logging.getLogger('codecarbon').setLevel(logging.ERROR)
        # tracking_mode='machine': carga de TODO el equipo (los tests corren en
        # subprocesos). force_cpu_power + force_mode_cpu_load: sin sudo no hay
        # `powermetrics`, así que la potencia se estima con la carga de CPU.
        self.tracker = OfflineEmissionsTracker(
            country_iso_code=pais, project_name=proyecto,
            measure_power_secs=1, tracking_mode='machine',
            force_cpu_power=tdp_cpu_w, force_mode_cpu_load=True,
            save_to_file=False, log_level='error',
        )
        self.tdp_cpu_w = tdp_cpu_w
        self.mediciones = mediciones
        self.traza = []
        self.ram_w = 3.0            # se corrige con el valor real tras la 1.ª fase

    def __getattr__(self, nombre):
        return getattr(self.tracker, nombre)

    def medir(self, fase, experimento, funcion, repeticion=1, extra=None):
        """Ejecuta funcion() midiendo su consumo en continuo.

        Devuelve lo que devuelva funcion(). La fila de la medición se anota en
        `mediciones` aunque funcion() lance una excepción.
        """
        nombre = '%s:%s:%d' % (experimento, fase, repeticion)
        muestreador = _Muestreador(self.tdp_cpu_w, self.ram_w, INTERVALO_S)
        self.tracker.start_task(nombre)
        muestreador.start()
        try:
            return funcion()
        finally:
            muestreador.parar()
            d = self.tracker.stop_task()
            self._anotar(d, fase, experimento, repeticion, muestreador, extra)

    def _anotar(self, d, fase, experimento, repeticion, muestreador, extra):
        if d.cpu_power:                 # tras la 1.ª fase ya se conoce el valor
            self.ram_w = d.ram_power or self.ram_w
        # Energía integrada de la traza (Wh -> kWh). Lo que dura cada muestra
        # (dt) multiplica a la potencia del instante en que se tomó.
        energia_traza = sum((p_cpu + p_ram) * dt
                            for _, _, p_cpu, p_ram, dt in muestreador.muestras) / 3.6e6
        factor = d.emissions / d.energy_consumed if d.energy_consumed else 0.0
        acumulada = 0.0
        for t, carga, p_cpu, p_ram, dt in muestreador.muestras:
            acumulada += (p_cpu + p_ram) * dt / 3.6e6
            self.traza.append({
                'experimento': experimento, 'fase': fase, 'repeticion': repeticion,
                't_s': round(t, 3), 'carga_cpu_pct': carga,
                'potencia_cpu_w': round(p_cpu, 3), 'potencia_ram_w': p_ram,
                'potencia_total_w': round(p_cpu + p_ram, 3),
                'energia_acumulada_wh': acumulada * 1e3,
                'emisiones_acumuladas_mg': acumulada * factor * 1e6,
            })
        potencias = [p_cpu + p_ram for _, _, p_cpu, p_ram, _ in muestreador.muestras]
        fila = {
            'experimento': experimento, 'fase': fase, 'repeticion': repeticion,
            'duracion_s': d.duration,
            'energia_kwh': d.energy_consumed,
            'energia_cpu_kwh': d.cpu_energy,
            'energia_ram_kwh': d.ram_energy,
            'emisiones_kg': d.emissions,
            'potencia_cpu_w': d.cpu_power,
            'potencia_ram_w': d.ram_power,
            # --- medición continua (muestreo de INTERVALO_S) ---
            'n_muestras': len(muestreador.muestras),
            'energia_traza_kwh': energia_traza,
            'emisiones_traza_kg': energia_traza * factor,
            'potencia_pico_w': max(potencias, default=0.0),
            'potencia_media_traza_w': (sum(potencias) / len(potencias)) if potencias else 0.0,
        }
        fila.update(extra or {})
        self.mediciones.append(fila)

    def guardar_traza(self, ruta, anexar=False):
        """Escribe las muestras en un CSV (una fila por muestra).

        Con anexar=True las añade al final del archivo (y vacía la lista en
        memoria), para ir guardando a medida que avanza una ejecución larga.
        """
        import csv
        import os
        if not self.traza:
            return
        nuevo = not (anexar and os.path.exists(ruta))
        with open(ruta, 'w' if nuevo else 'a', newline='') as f:
            escritor = csv.DictWriter(f, fieldnames=list(self.traza[0]))
            if nuevo:
                escritor.writeheader()
            escritor.writerows(self.traza)
        if anexar:
            self.traza = []
