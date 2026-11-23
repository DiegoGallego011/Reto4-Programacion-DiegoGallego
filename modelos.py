"""Entidades del dominio de Software FJ aplicando abstracción, herencia,
encapsulación y polimorfismo."""

from abc import ABC, abstractmethod
from datetime import datetime
from excepciones import (
    CapacidadInvalidaError,
    CancelacionNoPermitidaError,
    ClienteInvalidoError,
    ReservaInvalidaError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
)


class EntidadBase(ABC):
    """Clase abstracta base para todas las entidades del sistema."""

    def __init__(self, id_entidad: str):
        # Valida que el identificador no llegue vacío o solo con espacios
        if not id_entidad or not str(id_entidad).strip():
            raise ValueError("El identificador no puede estar vacío.")
        self._id = str(id_entidad).strip()
        self._fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def id(self) -> str:
        """Devuelve el identificador encapsulado de la entidad."""
        return self._id

    @property
    def fecha_creacion(self) -> str:
        """Devuelve la fecha y hora de creación del registro."""
        return self._fecha_creacion

    @abstractmethod
    def obtener_detalle(self) -> dict:
        """Cada subclase debe retornar sus datos principales en un diccionario."""
        pass


class Cliente(EntidadBase):
    """Representa a un cliente registrado con validación estricta de sus datos."""

    def __init__(self, id_cliente: str, nombre: str, correo: str, telefono: str):
        super().__init__(id_cliente)
        self._nombre = str(nombre).strip() if nombre is not None else ""
        self._correo = str(correo).strip() if correo is not None else ""
        self._telefono = str(telefono).strip() if telefono is not None else ""
        self.validar_datos()

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def correo(self) -> str:
        return self._correo

    @property
    def telefono(self) -> str:
        return self._telefono

    def validar_datos(self) -> None:
        """Verifica nombre, formato básico de correo y longitud del teléfono."""
        if len(self._nombre) < 3:
            raise ClienteInvalidoError(
                f"El nombre '{self._nombre}' debe tener al menos 3 caracteres."
            )
        if "@" not in self._correo or "." not in self._correo.split("@")[-1]:
            raise ClienteInvalidoError(
                f"El correo '{self._correo}' no tiene un formato válido."
            )
        if not self._telefono.isdigit() or len(self._telefono) < 7:
            raise ClienteInvalidoError(
                f"El teléfono '{self._telefono}' debe ser numérico y tener mínimo 7 dígitos."
            )

    def obtener_detalle(self) -> dict:
        return {
            "id": self._id,
            "nombre": self._nombre,
            "correo": self._correo,
            "telefono": self._telefono,
            "fecha_creacion": self._fecha_creacion,
        }


class Servicio(EntidadBase):
    """Clase abstracta para los distintos servicios que ofrece Software FJ."""

    def __init__(self, id_servicio: str, nombre: str, tarifa_base, disponible: bool = True):
        super().__init__(id_servicio)
        if not nombre or not str(nombre).strip():
            raise ServicioInvalidoError("El nombre del servicio es obligatorio.")

        # Conversión segura con encadenamiento de excepciones si llega un tipo no numérico
        try:
            tarifa_num = float(tarifa_base)
        except (TypeError, ValueError) as err:
            raise ServicioInvalidoError(
                f"La tarifa base '{tarifa_base}' no es un número válido."
            ) from err

        if tarifa_num <= 0:
            raise ServicioInvalidoError("La tarifa base debe ser mayor que cero.")

        self._nombre = str(nombre).strip()
        self._tarifa_base = tarifa_num
        self._disponible = bool(disponible)

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @property
    def disponible(self) -> bool:
        return self._disponible

    def cambiar_disponibilidad(self, estado: bool) -> None:
        """Habilita o deshabilita el servicio para nuevas reservas."""
        self._disponible = bool(estado)

    def _validar_calculo(self, horas, descuento: float, impuesto: float) -> tuple:
        """Valida los parámetros opcionales compartidos para el cálculo de costos."""
        try:
            horas_num = float(horas)
            desc_num = float(descuento)
            imp_num = float(impuesto)
        except (TypeError, ValueError) as err:
            raise ReservaInvalidaError(
                "Las horas, el descuento y el impuesto deben ser valores numéricos."
            ) from err

        if horas_num < 1.0:
            raise ReservaInvalidaError(
                f"La duración ({horas_num} h) debe ser de al menos 1 hora."
            )
        if not (0.0 <= desc_num <= 50.0):
            raise ReservaInvalidaError(
                f"El descuento ({desc_num}%) debe estar entre 0% y 50%."
            )
        if not (0.0 <= imp_num <= 30.0):
            raise ReservaInvalidaError(
                f"El impuesto ({imp_num}%) debe estar entre 0% y 30%."
            )
        return horas_num, desc_num, imp_num

    def _aplicar_descuento_e_impuesto(
        self, subtotal: float, descuento: float = 0.0, impuesto: float = 0.0
    ) -> float:
        """Aplica primero el descuento y luego el impuesto sobre el subtotal."""
        con_descuento = subtotal * (1.0 - descuento / 100.0)
        total = con_descuento * (1.0 + impuesto / 100.0)
        return round(total, 2)

    @abstractmethod
    def validar_parametros(self) -> None:
        pass

    @abstractmethod
    def calcular_costo(
        self, horas: float, descuento: float = 0.0, impuesto: float = 0.0
    ) -> float:
        """Método sobrecargado mediante parámetros opcionales (solo horas, con descuento y/o IVA)."""
        pass

    @abstractmethod
    def describir_servicio(self) -> str:
        pass


class ReservaSala(Servicio):
    """Servicio de alquiler de salas físicas con opción de proyector."""

    CARGO_PROYECTOR = 15000.0

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base,
        capacidad,
        proyector: bool = True,
    ):
        super().__init__(id_servicio, nombre, tarifa_base)
        try:
            self._capacidad = int(capacidad)
        except (TypeError, ValueError) as err:
            raise CapacidadInvalidaError(
                f"La capacidad '{capacidad}' debe ser un número entero."
            ) from err
        self._proyector = bool(proyector)
        self.validar_parametros()

    def validar_parametros(self) -> None:
        if self._capacidad <= 0:
            raise CapacidadInvalidaError(
                f"La capacidad de la sala ({self._capacidad}) debe ser mayor a 0."
            )

    def calcular_costo(
        self, horas: float, descuento: float = 0.0, impuesto: float = 0.0
    ) -> float:
        h, desc, imp = self._validar_calculo(horas, descuento, impuesto)
        extra = self.CARGO_PROYECTOR if self._proyector else 0.0
        subtotal = (self._tarifa_base * h) + extra
        return self._aplicar_descuento_e_impuesto(subtotal, desc, imp)

    def describir_servicio(self) -> str:
        proy = "con proyector" if self._proyector else "sin proyector"
        return f"Sala '{self._nombre}' para {self._capacidad} personas ({proy})."

    def obtener_detalle(self) -> dict:
        return {
            "id": self._id,
            "tipo": "Reserva de Sala",
            "nombre": self._nombre,
            "tarifa_base": self._tarifa_base,
            "capacidad": self._capacidad,
            "proyector": self._proyector,
        }


class AlquilerEquipo(Servicio):
    """Servicio de préstamo de equipos tecnológicos con seguro básico del 5%."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base,
        tipo_equipo: str,
        deposito: float = 50000.0,
    ):
        super().__init__(id_servicio, nombre, tarifa_base)
        self._tipo_equipo = str(tipo_equipo).strip() if tipo_equipo else ""
        try:
            self._deposito = float(deposito)
        except (TypeError, ValueError) as err:
            raise ServicioInvalidoError("El depósito debe ser un valor numérico.") from err
        self.validar_parametros()

    def validar_parametros(self) -> None:
        if not self._tipo_equipo:
            raise ServicioInvalidoError("Debe especificar el tipo de equipo.")
        if self._deposito < 0:
            raise ServicioInvalidoError("El depósito de garantía no puede ser negativo.")

    def calcular_costo(
        self, horas: float, descuento: float = 0.0, impuesto: float = 0.0
    ) -> float:
        h, desc, imp = self._validar_calculo(horas, descuento, impuesto)
        base = self._tarifa_base * h
        seguro = base * 0.05
        return self._aplicar_descuento_e_impuesto(base + seguro, desc, imp)

    def describir_servicio(self) -> str:
        return f"Alquiler de {self._tipo_equipo} ('{self._nombre}'), depósito ${self._deposito:,.0f}."

    def obtener_detalle(self) -> dict:
        return {
            "id": self._id,
            "tipo": "Alquiler de Equipo",
            "nombre": self._nombre,
            "equipo": self._tipo_equipo,
            "deposito": self._deposito,
        }


class AsesoriaEspecializada(Servicio):
    """Servicio de consultoría técnica con tarifa ajustada según el nivel del consultor."""

    MULTIPLICADORES = {"Junior": 1.0, "Mid": 1.25, "Senior": 1.6, "Expert": 2.0}

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base,
        area: str,
        nivel: str = "Senior",
    ):
        super().__init__(id_servicio, nombre, tarifa_base)
        self._area = str(area).strip() if area else ""
        self._nivel = str(nivel).strip() if nivel else ""
        self.validar_parametros()

    def validar_parametros(self) -> None:
        if not self._area:
            raise ServicioInvalidoError("El área de la asesoría no puede quedar vacía.")
        if self._nivel not in self.MULTIPLICADORES:
            validos = ", ".join(self.MULTIPLICADORES.keys())
            raise ServicioInvalidoError(
                f"Nivel '{self._nivel}' no válido. Opciones permitidas: {validos}."
            )

    def calcular_costo(
        self, horas: float, descuento: float = 0.0, impuesto: float = 0.0
    ) -> float:
        h, desc, imp = self._validar_calculo(horas, descuento, impuesto)
        factor = self.MULTIPLICADORES[self._nivel]
        subtotal = (self._tarifa_base * h) * factor
        return self._aplicar_descuento_e_impuesto(subtotal, desc, imp)

    def describir_servicio(self) -> str:
        return f"Asesoría en {self._area} nivel {self._nivel} ('{self._nombre}')."

    def obtener_detalle(self) -> dict:
        return {
            "id": self._id,
            "tipo": "Asesoría Especializada",
            "nombre": self._nombre,
            "area": self._area,
            "nivel": self._nivel,
        }


class Reserva(EntidadBase):
    """Vincula un cliente con un servicio, controla su estado y liquida el costo."""

    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, horas):
        super().__init__(id_reserva)
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un servicio válido.")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{servicio.nombre}' no está disponible en este momento."
            )

        try:
            horas_num = float(horas)
        except (TypeError, ValueError) as err:
            raise ReservaInvalidaError(
                f"El valor de horas '{horas}' no es numérico."
            ) from err

        if horas_num < 1.0:
            raise ReservaInvalidaError(
                f"Duración insuficiente ({horas_num} h). La reserva mínima es de 1 hora."
            )

        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas_num
        self._estado = "PENDIENTE"
        self._total = 0.0

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def total(self) -> float:
        return self._total

    def procesar_y_confirmar(self, descuento: float = 0.0, impuesto: float = 0.0) -> float:
        """Calcula el valor final según las reglas del servicio y confirma la reserva."""
        if self._estado != "PENDIENTE":
            raise ReservaInvalidaError(
                f"No se puede confirmar la reserva {self._id} porque está en estado {self._estado}."
            )
        self._total = self._servicio.calcular_costo(self._horas, descuento, impuesto)
        self._estado = "CONFIRMADA"
        return self._total

    def cancelar(self) -> None:
        """Cambia el estado a CANCELADA si la reserva estaba confirmada o pendiente."""
        if self._estado == "CANCELADA":
            raise CancelacionNoPermitidaError(
                f"La reserva {self._id} ya fue cancelada anteriormente."
            )
        self._estado = "CANCELADA"

    def obtener_detalle(self) -> dict:
        return {
            "id_reserva": self._id,
            "cliente": self._cliente.nombre,
            "servicio": self._servicio.nombre,
            "horas": self._horas,
            "estado": self._estado,
            "total": self._total,
        }
