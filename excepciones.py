"""Excepciones personalizadas para el sistema de gestión de Software FJ."""


class ErrorSoftwareFJ(Exception):
    """Clase base para todos los errores propios de la aplicación."""
    pass


class ClienteInvalidoError(ErrorSoftwareFJ):
    """Se lanza cuando los datos de un cliente no cumplen las validaciones."""
    pass


class ServicioInvalidoError(ErrorSoftwareFJ):
    """Se lanza cuando un servicio recibe parámetros o tarifas incorrectas."""
    pass


class CapacidadInvalidaError(ServicioInvalidoError):
    """Se lanza cuando la capacidad de una sala es menor o igual a cero."""
    pass


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """Se lanza al intentar reservar un servicio que está deshabilitado."""
    pass


class ReservaInvalidaError(ErrorSoftwareFJ):
    """Se lanza cuando una reserva tiene datos faltantes, horas inválidas o cálculo erróneo."""
    pass


class CancelacionNoPermitidaError(ErrorSoftwareFJ):
    """Se lanza si se intenta cancelar una reserva que no está confirmada."""
    pass
