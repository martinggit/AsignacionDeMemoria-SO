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

    def correr(self, tiempo_max):
        print(f"Simulación iniciada con {len(self.procesos)} procesos.\n")
        while self.tiempo <= tiempo_max:
            print(f"\nTiempo: {self.tiempo}")
            print("Estado de memoria:", self.particiones)

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

            self.tiempo += 1

        print("\n Simulación finalizada")
