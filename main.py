from simulador import Simulador
from politicas.first_fit import first_fit
from politicas.best_fit import best_fit
from politicas.next_fit import next_fit
from politicas.worst_fit import worst_fit
import os
#Parametros
memoria_total = int(input("Tamaño de memoria disponible: "))

# Mostrar opciones al usuario
print("Seleccione estrategia de asignación de particiones:")
print("1 - first_fit")
print("2 - best_fit")
print("3 - next_fit")
print("4 - worst_fit")

opcion = input("Ingrese el número de la estrategia: ")

politicas = {
    "1": first_fit,
    "2": best_fit,
    "3": next_fit,
    "4": worst_fit
}

politica = politicas.get(opcion)
if politica is None:
    print("Opción no válida, usando first_fit por defecto")
    politica = first_fit

# Tiempo que se tarda un proceso en cargar en memoria
t_carga = int(input("Ingrese tiempo de carga promedio: "))
# Tiempo que se tarda en seleccionar una partición
t_seleccion = int(input("Ingrese tiempo de selección de partición: "))
# Tiempo que se tarda en liberar la partición una vez que el proceso termina
t_liberacion = int(input("Ingrese tiempo de liberación de partición: "))

# Buscar todos los archivos tanda*.json en la carpeta
archivos_tanda = [f for f in os.listdir(".") if f.startswith("tanda") and f.endswith(".json")]

if not archivos_tanda:
    print("No se encontraron archivos de tandas en la carpeta.")
    exit(1)

print("Seleccione la tanda de procesos:")
for i, archivo in enumerate(archivos_tanda, start=1):
    print(f"{i} - {archivo}")

tanda_opcion = input("Ingrese el número de la tanda: ")

try:
    archivo = archivos_tanda[int(tanda_opcion) - 1]
except (ValueError, IndexError):
    print("Opción no válida, usando la primera tanda encontrada por defecto")
    archivo = archivos_tanda[0]

# Crear y correr simulador
sim = Simulador(
    memoria_total=memoria_total,
    archivo_procesos=archivo,
    politica=politica,
    t_carga = t_carga,
    t_seleccion = t_seleccion,
    t_liberacion = t_liberacion,
)

sim.correr()

