#Simulador va a manejar la memoria (lista de particiones)
#Leer los procesos desde el json y simular el paso del tiempo según la política elegida

import json
from particion import Particion
from proceso import Proceso

class Simulador:
    def __init__(self, memoria_total, archivo_procesos, politica, t_carga=0, t_seleccion=0, t_liberacion=0, archivo_log="eventos.txt"):
        self.memoria_total = memoria_total
        self.particiones = [Particion(0, memoria_total)]  # arranca con 1 partición libre
        self.procesos = self._cargar_procesos(archivo_procesos)
        self.tiempo = 0
        self.politica = politica
        self.t_carga = t_carga
        self.t_seleccion = t_seleccion
        self.t_liberacion = t_liberacion
        self.pendientes =[] # Cola de espera, si un proceso no entra lo guardo hasta que se libere memoria
        self.archivo_log = archivo_log
        self.ife_total = 0  # índice de fragmentación externa 


        with open(self.archivo_log, "w", encoding="utf-8") as f:
            f.write("Simulación de eventos de memoria\n\n") 


    def _log_evento(self, tipo, descripcion):
        with open(self.archivo_log, "a", encoding="utf-8") as f:
            f.write(f"[Tiempo {self.tiempo}] [{tipo}] {descripcion}\n")

    def _log_memoria(self):
        estado = " | ".join(str(p) for p in self.particiones)
        self._log_evento("MEMORIA", f"Estado actual → [{estado}]")

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

        # evento: selección de partición
        self._log_evento("SELECCIÓN", f"Seleccionada {particion} para {proceso.nombre} (t_sel={self.t_seleccion})")

        # asignar el proceso
        particion.asignar(proceso, self.tiempo, self.t_carga, self.t_seleccion, self.t_liberacion)
        
        # evento: carga del proceso (cuando realmente empieza a residir en memoria)
        inicio_residencia = proceso.inicio + self.t_carga
        self._log_evento("CARGA", f"{proceso.nombre} cargado; inicio_residencia={inicio_residencia} (t_carga={self.t_carga})")
        
        print(f"Asignado {proceso.nombre} en {particion}")
        print(f"→ Datos del proceso {proceso.nombre}: inicio={proceso.inicio}, fin={proceso.fin}")
        print("Estado de memoria:", self.particiones)
        self._log_evento("ASIGNACIÓN", f"{proceso.nombre} asignado a {particion}")
        self._log_memoria()

    def merge_particiones(self):
        i = 0
        while i < len(self.particiones) - 1:
            actual = self.particiones[i]
            siguiente = self.particiones[i + 1]
            if actual.libre and siguiente.libre:
                # fusionar
                actual.size += siguiente.size
                self.particiones.pop(i + 1)
                self._log_evento("MERGE", f"Se fusionaron particiones libres en {actual}")
            else:
                i += 1
    
    def calcular_memoria_libre(self):
        return sum(p.size for p in self.particiones if p.libre)
    
    def correr(self):
        print(f"Simulación iniciada con {len(self.procesos)} procesos.\n")
        while True:
            print(f"\nTiempo: {self.tiempo}")
            print("Estado de memoria:", self.particiones)

            #I.F.E. = P( memoria no asignada * tiempo que permanece en esa condición). "Mientras haya trabajos esperando parasu ejecución"
            # Calcular IFE si hay procesos esperando
            if self.pendientes:
                memoria_libre = self.calcular_memoria_libre()
                self.ife_total += memoria_libre
                print(f"IFE acumulado: {self.ife_total}")

            # Liberar procesos terminados
            for part in self.particiones:
                if not part.libre and part.t_fin == self.tiempo:
                    print(f"Liberando {part.proceso.nombre} de {part}")
                    self._log_evento("LIBERACIÓN", f"{part.proceso.nombre} liberó {part}")
                    part.liberar()
                    self.merge_particiones()
                    self._log_memoria()

            # Llegan procesos en este instante
            for proceso in [p for p in self.procesos if p.llegada == self.tiempo]:
                print(f"Llega {proceso}")
                self._log_evento("LLEGADA", f"Proceso {proceso.nombre} llega al sistema")
                part = self.politica(self.particiones, proceso)
                if part:
                    self.asignar_particion(part, proceso)
                else:
                    print(f"No hay espacio para {proceso.nombre}, queda en espera.")
                    self._log_evento("ESPERA", f"No hay espacio para {proceso.nombre}, queda en espera")
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
        self._log_evento("FIN", "Simulación finalizada")

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

        print(f"Índice de Fragmentación Externa total = {self.ife_total}")
        
        # Tiempo de retorno de la tanda (batch)
        llegada_min = min(p.llegada for p in self.procesos)
        fin_max = max(p.fin for p in self.procesos if p.fin is not None)
        tanda_tr = fin_max - llegada_min
        print(f"\nTiempo de Retorno de la tanda = {tanda_tr}")
        self._log_evento("RESUMEN", f"Tiempo de Retorno de la tanda = {tanda_tr}")

