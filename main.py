"""Script principal con 12 operaciones simuladas (casos válidos y fallidos)
para comprobar la estabilidad y el manejo de excepciones de Software FJ."""

from excepciones import (
    CancelacionNoPermitidaError,
    CapacidadInvalidaError,
    ClienteInvalidoError,
    ReservaInvalidaError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
)
from gestion import GestionSoftwareFJ
from modelos import AlquilerEquipo, AsesoriaEspecializada, ReservaSala


def ejecutar_simulaciones():
    sistema = GestionSoftwareFJ("software_fj.log")
    c1 = s_sala = s_equipo = s_asesoria = None

    print("\n--- Inicio de simulaciones Software FJ ---\n")

    # Operación 1: Registro válido de cliente (try/except/else)
    try:
        c1 = sistema.registrar_cliente(
            "CLI-001", "Laura Martínez", "laura.martinez@correo.com", "3104567890"
        )
    except ClienteInvalidoError as err:
        print(f"[Op 1] Error inesperado: {err}")

    # Operación 2: Registro inválido de cliente (correo sin arroba)
    try:
        sistema.registrar_cliente(
            "CLI-002", "Andrés Ruiz", "andresruiz_sin_arroba.com", "3159876543"
        )
    except ClienteInvalidoError as err:
        print(f"[Op 2] Error controlado: {err}")

    # Operación 3: Creación válida de ReservaSala
    try:
        s_sala = sistema.registrar_servicio(
            ReservaSala, "SAL-01", "Sala de Juntas Norte", 45000, 12, True
        )
    except ServicioInvalidoError as err:
        print(f"[Op 3] Error inesperado: {err}")

    # Operación 4: Creación inválida de ReservaSala (capacidad 0)
    try:
        sistema.registrar_servicio(
            ReservaSala, "SAL-02", "Sala Auxiliar", 20000, 0, False
        )
    except CapacidadInvalidaError as err:
        print(f"[Op 4] Error controlado: {err}")

    # Operación 5: Creación válida de AlquilerEquipo y AsesoriaEspecializada
    try:
        s_equipo = sistema.registrar_servicio(
            AlquilerEquipo, "EQ-01", "Portátil Core i7", 25000, "Laptop", 50000
        )
        s_asesoria = sistema.registrar_servicio(
            AsesoriaEspecializada, "ASE-01", "Arquitectura Cloud", 80000, "Cloud", "Senior"
        )
    except ServicioInvalidoError as err:
        print(f"[Op 5] Error inesperado: {err}")

    # Operación 6: Creación inválida de servicio con encadenamiento (tarifa no numérica)
    try:
        sistema.registrar_servicio(
            AlquilerEquipo, "EQ-ERR", "Proyector 4K", "gratis", "Proyector"
        )
    except ServicioInvalidoError as err:
        print(f"[Op 6] Error encadenado controlado: {err} (origen: {type(err.__cause__).__name__})")

    # Operación 7: Reserva exitosa con descuento (10%) e IVA (19%) -> Total esperado: $208,845.00
    try:
        sistema.crear_reserva("RES-001", c1, s_sala, horas=4, descuento=10, impuesto=19)
    except (ReservaInvalidaError, ServicioNoDisponibleError) as err:
        print(f"[Op 7] Error inesperado: {err}")

    # Operación 8: Reserva exitosa con parámetros por defecto (sobrecarga sin descuento ni IVA) -> Total: $52,500.00
    try:
        sistema.crear_reserva("RES-002", c1, s_equipo, horas=2)
    except (ReservaInvalidaError, ServicioNoDisponibleError) as err:
        print(f"[Op 8] Error inesperado: {err}")

    # Operación 9: Reserva fallida por duración menor a 1 hora
    try:
        sistema.crear_reserva("RES-003", c1, s_equipo, horas=0.5)
    except ReservaInvalidaError as err:
        print(f"[Op 9] Error controlado: {err}")

    # Operación 10: Reserva fallida con encadenamiento (horas como texto)
    try:
        sistema.crear_reserva("RES-004", c1, s_equipo, horas="dos")
    except ReservaInvalidaError as err:
        print(f"[Op 10] Error encadenado controlado: {err} (origen: {type(err.__cause__).__name__})")

    # Operación 11: Reserva fallida sobre servicio deshabilitado
    try:
        sistema.cambiar_disponibilidad_servicio(s_asesoria, False)
        sistema.crear_reserva("RES-005", c1, s_asesoria, horas=3)
    except ServicioNoDisponibleError as err:
        print(f"[Op 11] Error controlado: {err}")

    # Operación 12: Cancelación exitosa y posterior intento inválido de re-cancelación
    try:
        sistema.cancelar_reserva("RES-001")
    except (ReservaInvalidaError, CancelacionNoPermitidaError) as err:
        print(f"[Op 12a] Error inesperado: {err}")

    try:
        sistema.cancelar_reserva("RES-001")
    except CancelacionNoPermitidaError as err:
        print(f"[Op 12b] Error controlado: {err}")

    resumen = sistema.resumen_estado()
    print(
        f"\n--- Fin de simulaciones | Clientes: {resumen['clientes']} | "
        f"Servicios: {resumen['servicios']} | Reservas: {resumen['reservas']} ---"
    )
    print("Revisa el detalle completo en el archivo 'software_fj.log'.")


if __name__ == "__main__":
    ejecutar_simulaciones()