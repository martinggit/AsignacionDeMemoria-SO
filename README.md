# 🖥️ Simulador de Asignación de Memoria Dinámica

## 📌 Descripción
Este proyecto implementa un **simulador de asignación de memoria dinámica con particiones y asignación contigua**.  
La memoria arranca como un único bloque libre y, a medida que se cargan procesos, se divide en particiones ocupadas y libres.  
Cuando los procesos terminan, las particiones se liberan y se realiza un **merge** de particiones libres adyacentes para reducir la fragmentación externa.

El simulador soporta diferentes **estrategias de ubicación de procesos**:

- **First Fit** → primera partición libre que alcanza.  
- **Best Fit** → la partición libre más ajustada al tamaño del proceso.  
- **Next Fit** → similar a First Fit, pero continúa desde la última posición usada.  
- **Worst Fit** → la partición libre más grande.  

---

## ⚙️ Funcionalidades
- Cargar procesos desde un archivo JSON (ejemplo: `tanda1.json`).  
- Simular paso a paso la ejecución en memoria.  
- Manejar una **cola de espera** cuando no hay suficiente espacio.  
- Dividir particiones dinámicamente y fusionarlas al liberar.  
- Calcular métricas al finalizar:  
  - Tiempo de retorno de cada proceso.  
  - Tiempo medio de retorno.  
  - Índice de fragmentación externa (IFE).  
  - Tiempo de retorno de la tanda (batch).  
- Guardar un **log de eventos** (`eventos.txt`) con detalle de cada asignación, liberación y estado de memoria.  

---

## 🚀 Ejecución
El simulador **no requiere instalar librerías externas** (solo Python 3).

### Clonar el repositorio
```bash
git clone https://github.com/martinggit/AsignacionDeMemoria-SO.git
cd AsignacionDeMemoria-SO
```
### Se ejecuta con:
```bash
python main.py
```

### Ejemplo de ejecución
```bash
Tamaño de memoria disponible: 100
Seleccione estrategia de asignación de particiones:
1 - first_fit
2 - best_fit
3 - next_fit
4 - worst_fit
Ingrese el número de la estrategia: 1
Ingrese tiempo de carga promedio: 2
Ingrese tiempo de selección de partición: 2
Ingrese tiempo de liberación de partición: 2
Ingrese el nombre de la tanda de procesos (ej: tanda1.json): tanda1.json
Ingrese tiempo máximo de simulación: 100 
```
⚠️ Nota: El tiempo máximo de simulación debe ser suficientemente grande para asegurar que todos los procesos finalicen. Se usa solo como límite de seguridad.
