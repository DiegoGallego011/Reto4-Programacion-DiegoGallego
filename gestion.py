
"""Módulo controlador en memoria y configuración del archivo de logs."""

import logging
from excepciones import (
    CancelacionNoPermitidaError,
    ClienteInvalidoError,
    ErrorSoftwareFJ,
    ReservaInvalidaError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
)
from modelos import Cliente, Reserva, Servicio


def configurar_logger(ruta_log: str = "software_fj.log") -> logging.Logger:
    """Configura el registro de eventos y errores en archivo UTF-8 y consola."""
    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.INFO)

    # Evita duplicar salidas si se importa el módulo más de una vez
    if not logger.handlers:
        formato = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        archivo_handler = logging.FileHandler(ruta_log, mode="w", encoding="utf-8")
        archivo_handler.setLevel(logging.INFO)
        archivo_handler.setFormatter(formato)

        consola_handler = logging.StreamHandler()
        consola_handler.setLevel(logging.INFO)
        consola_handler.setFormatter(formato)

        logger.addHandler(archivo_handler)
        logger.addHandler(consola_handler)
    return logger


class GestionSoftwareFJ:
    """Administra clientes, servicios y reservas usando listas en memoria."""

    def __init__(self, ruta_log: str = "software_fj.log"):
        self._clientes = []
        self._servicios = []
        self._reservas = []
        self._logger = configurar_logger(ruta_log)
        self._logger.info("Sistema Software FJ iniciado correctamente (almacenamiento en memoria).")

    def registrar_cliente(self, id_cli: str, nombre: str, correo: str, telefono: str):
        """Registra un cliente usando try/except/else."""
        try:
            cliente = Cliente(id_cli, nombre, correo, telefono)
        except ClienteInvalidoError as err:
            self._logger.error(f"Registro de cliente rechazado ({id_cli}): {err}")
            raise
        except Exception as err:
            self._logger.error(f"Error inesperado al registrar cliente ({id_cli}): {err}")
            raise ErrorSoftwareFJ("Fallo interno al crear el cliente.") from err
        else:
            self._clientes.append(cliente)
            self._logger.info(
                f"Cliente registrado: ID={cliente.id}, Nombre='{cliente.nombre}'."
            )
            return cliente

    def registrar_servicio(self, clase_servicio, *args, **kwargs):
        """Instancia y registra cualquier subclase de Servicio usando try/except/else."""
        try:
            servicio = clase_servicio(*args, **kwargs)
            if not isinstance(servicio, Servicio):
                raise ServicioInvalidoError("El objeto creado no hereda de Servicio.")
        except ServicioInvalidoError as err:
            causa = f" | Causa original: {type(err.__cause__).__name__}: {err.__cause__}" if err.__cause__ else ""
            self._logger.error(f"Registro de servicio rechazado: {err}{causa}")
            raise
        except Exception as err:
            self._logger.error(f"Error inesperado al registrar servicio: {err}")
            raise ErrorSoftwareFJ("Fallo interno al crear el servicio.") from err
        else:
            self._servicios.append(servicio)
            self._logger.info(
                f"Servicio registrado: ID={servicio.id} | {servicio.describir_servicio()}"
            )
            return servicio

    def cambiar_disponibilidad_servicio(self, servicio: Servicio, estado: bool) -> None:
        """Actualiza y registra en el log el cambio de estado de un servicio."""
        servicio.cambiar_disponibilidad(estado)
        etiqueta = "DISPONIBLE" if estado else "NO DISPONIBLE"
        self._logger.info(f"Servicio {servicio.id} ('{servicio.nombre}') cambiado a {etiqueta}.")

    def crear_reserva(
        self,
        id_res: str,
        cliente: Cliente,
        servicio: Servicio,
        horas,
        descuento: float = 0.0,
        impuesto: float = 0.0,
    ):
        """Crea y liquida una reserva usando try/except/else/finally."""
        try:
            reserva = Reserva(id_res, cliente, servicio, horas)
            total = reserva.procesar_y_confirmar(descuento=descuento, impuesto=impuesto)
        except (ReservaInvalidaError, ServicioNoDisponibleError) as err:
            causa = f" | Causa original: {type(err.__cause__).__name__}: {err.__cause__}" if err.__cause__ else ""
            self._logger.warning(f"Reserva {id_res} rechazada: {err}{causa}")
            raise
        except Exception as err:
            self._logger.error(f"Error crítico en reserva {id_res}: {err}")
            raise ErrorSoftwareFJ("Fallo inesperado al procesar la reserva.") from err
        else:
            self._reservas.append(reserva)
            self._logger.info(
                f"Reserva {reserva.id} confirmada | Cliente: '{cliente.nombre}' | "
                f"Servicio: '{servicio.nombre}' | Total: ${total:,.2f}"
            )
            return reserva
        finally:
            self._logger.info(f"Cierre de transacción para la solicitud de reserva {id_res}.")

    def cancelar_reserva(self, id_res: str) -> None:
        """Busca y cancela una reserva registrada usando try/except/else."""
        try:
            reserva = next((r for r in self._reservas if r.id == id_res), None)
            if reserva is None:
                raise ReservaInvalidaError(f"No existe ninguna reserva con ID '{id_res}'.")
            reserva.cancelar()
        except (ReservaInvalidaError, CancelacionNoPermitidaError) as err:
            self._logger.warning(f"No se pudo cancelar la reserva {id_res}: {err}")
            raise
        else:
            self._logger.info(f"Reserva {id_res} cancelada correctamente.")

    def resumen_estado(self) -> dict:
        """Retorna el conteo final de registros almacenados en memoria."""
        return {
            "clientes": len(self._clientes),
            "servicios": len(self._servicios),
            "reservas": len(self._reservas),
        }
