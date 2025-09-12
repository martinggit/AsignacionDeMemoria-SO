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

# Selección de la tanda de procesos
print("Seleccione la tanda de procesos (1 a 5):")
for i in range(1, 6):
    print(f"{i} - tanda{i}.json")

tanda_opcion = input("Ingrese el número de la tanda: ")
if tanda_opcion not in ["1", "2", "3", "4", "5"]:
    print("Opción no válida, usando tanda1.json por defecto")
    tanda_opcion = "1"

archivo = f"tanda{tanda_opcion}.json"
if not os.path.exists(archivo):
    print(f"Archivo {archivo} no existe, asegurate de tenerlo en la carpeta")
    exit(1)

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

