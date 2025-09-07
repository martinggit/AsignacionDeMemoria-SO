#Simulador va a manejar la memoria (lista de particiones)
#Leer los procesos desde el json y simular el paso del tiempo según la política elegida

import json
from particion import Particion
from proceso import Proceso

class Simulador:
    def __init__(self, memoria_total, archivo_procesos, politica, t_carga=0, t_seleccion=0, t_liberacion=0):
        self.memoria_total = memoria_total
        self.particiones = [Particion(0, memoria_total)]  # arranca con 1 partición libre
        self.procesos = self._cargar_procesos(archivo_procesos)
        self.tiempo = 0
        self.politica = politica
        self.t_carga = t_carga
        self.t_seleccion = t_seleccion
        self.t_liberacion = t_liberacion
        self.pendientes =[] # Cola de espera, si un proceso no entra lo guardo hasta que se libere memoria
        self.fragmentaciones = []  # guardamos los valores de frag externa en cada t

    def _cargar_procesos(self, archivo):
        with open(archivo, "r") as f:
            data = json.load(f)
        procesos = []
        for p in data:
            procesos.append(
                Proceso(
                    nombre=p["nombre"],
                    size=p["size"],
                    duracion=p["duracion"],
                    llegada=p.get("llegada", 0),
                )
            )
        return procesos

    def asignar_particion(self, particion, proceso):
        # si sobra espacio, dividir la partición
        if particion.size > proceso.size:
            nueva = Particion(
                inicio=particion.inicio + proceso.size,
                size=particion.size - proceso.size
            )
            particion.size = proceso.size
            idx = self.particiones.index(particion)
            self.particiones.insert(idx + 1, nueva)

        # asignar el proceso
        particion.asignar(proceso, self.tiempo, self.t_carga, self.t_seleccion, self.t_liberacion)
        print(f"Asignado {proceso.nombre} en {particion}")
        print(f"→ Datos del proceso {proceso.nombre}: inicio={proceso.inicio}, fin={proceso.fin}")

    def merge_particiones(self):
        i = 0
        while i < len(self.particiones) - 1:
            actual = self.particiones[i]
            siguiente = self.particiones[i + 1]
            if actual.libre and siguiente.libre:
                # fusionar
                actual.size += siguiente.size
                self.particiones.pop(i + 1)
            else:
                i += 1

    # Frag. Ext. = (Memoria Libre - mayor hueco libre) / Memoria Total
    def calcular_fragmentacion_externa(self):
        memoria_libre = sum(p.size for p in self.particiones if p.libre)
        if memoria_libre == 0:
            return 0.0

        mayor_hueco = max((p.size for p in self.particiones if p.libre), default=0)
        frag = (memoria_libre - mayor_hueco) / self.memoria_total * 100
        return frag
    
    def correr(self, tiempo_max):
        print(f"Simulación iniciada con {len(self.procesos)} procesos.\n")
        while self.tiempo <= tiempo_max:
            print(f"\nTiempo: {self.tiempo}")
            print("Estado de memoria:", self.particiones)

            # Calcular frag externa 
            frag = self.calcular_fragmentacion_externa()
            self.fragmentaciones.append(frag)
            print(f"Fragmentación externa: {frag:.2f}%")

            # Liberar procesos terminados
            for part in self.particiones:
                if not part.libre and part.t_fin == self.tiempo:
                    print(f"Liberando {part.proceso.nombre} de {part}")
                    part.liberar()
                    self.merge_particiones()

            # Llegan procesos en este instante
            for proceso in [p for p in self.procesos if p.llegada == self.tiempo]:
                print(f"Llega {proceso}")
                part = self.politica(self.particiones, proceso)
                if part:
                    self.asignar_particion(part, proceso)
                else:
                    print(f"No hay espacio para {proceso.nombre}, queda en espera.")
                    self.pendientes.append(proceso)

            # Reintentar asignar pendientes
            for proceso in list(self.pendientes): 
                part = self.politica(self.particiones, proceso)
                if part:
                    self.asignar_particion(part, proceso)
                    self.pendientes.remove(proceso)

            # Condición de corte anticipado
            if all(p.fin is not None for p in self.procesos) and not self.pendientes:
                ultimo_fin = max(p.fin for p in self.procesos if p.fin is not None)
                if self.tiempo >= ultimo_fin:
                    break

            self.tiempo += 1

        self.merge_particiones()
        print("Estado final de memoria:", self.particiones)
        print("\n Simulación finalizada")

        # Calcular estadísticas
        print("\n--- TIEMPOS ---")
        tiempos_retorno = []
        for p in self.procesos:
            if p.fin is not None:
                t_retorno = p.fin - p.llegada
                tiempos_retorno.append(t_retorno)
                print(f"{p.nombre}: Retorno={t_retorno} (Inicio={p.inicio}, Fin={p.fin}, Llegada={p.llegada})")

        if tiempos_retorno:
            promedio = sum(tiempos_retorno) / len(tiempos_retorno)
            print(f"\nTiempo Medio de Retorno = {promedio:.2f}")

        # Promedio de fragmentación externa
        if self.fragmentaciones:
            promedio_frag = sum(self.fragmentaciones) / len(self.fragmentaciones)
            max_frag = max(self.fragmentaciones)
            print(f"\nFragmentación Externa Promedio = {promedio_frag:.2f}%")
            print(f"Fragmentación Externa Máxima = {max_frag:.2f}%")
