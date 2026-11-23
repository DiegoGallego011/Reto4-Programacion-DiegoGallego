# Reto4-Programacion-DiegoGallego
Evaluacion Reto 4 de Programacion
# Sistema de Gestión de Clientes, Servicios y Reservas - Software FJ

Proyecto correspondiente a la **Fase 4 – Componente práctico (Prácticas simuladas)** del curso Programación (213023) de la UNAD.

## Descripción
Aplicación en Python orientada a objetos, sin uso de bases de datos, que administra clientes, tres tipos de servicios (salas, alquiler de equipos y asesorías especializadas) y reservas mediante listas en memoria. Todos los eventos y errores se registran en el archivo `software_fj.log`.

## Estructura del proyecto
- `excepciones.py`: Jerarquía de excepciones personalizadas del dominio.
- `modelos.py`: Clases abstractas (`EntidadBase`, `Servicio`), clases concretas (`Cliente`, `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada`, `Reserva`) con validaciones y cálculo de costos con parámetros opcionales.
- `gestion.py`: Controlador en memoria (`GestionSoftwareFJ`) y configuración del módulo `logging`.
- `main.py`: Script con 12 operaciones simuladas (válidas y fallidas) para probar estabilidad, bloques `try/except/else/finally` y encadenamiento de excepciones.

## Ejecución
Requiere Python 3.10 o superior (solo usa librerías estándar):

```bash
python main.py
