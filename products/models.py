"""
Modelos de Productos y Historial de Precios.

Este módulo contiene los modelos para la gestión de productos,
tarifas, rangos de horas e historial de precios.

Estructura:
- Rate: Tarifas del sistema (ej: 'Tarifa Normal', 'Tarifa Especial')
- HourRange: Rangos de horas para productos (ej: 1 hora, 2 horas)
- Product: Productos combinando tarifa + inmueble + rango de horas
- Price: Historial de precios de un producto (con vigencia)
- Price_Additional_Hour: Precio por hora adicional

Historial de Precios:
Cada producto puede tener múltiples precios a lo largo del tiempo.
El sistema mantiene un historial completo con:
- is_active: Indica cuál es el precio vigente
- valid_from: Fecha desde la cual es válido
- valid_to: Fecha hasta la cual fue válido (null = vigente)
- created_at: Fecha de creación del registro

Autor: Dilan Torrez
Fecha: 2026
"""

from django.contrib.postgres.fields import ArrayField
from django.db import models
from rooms.models import Room
from customers.models import Customer_type


class Rate(models.Model):
    """
    Modelo de tarifas del sistema.

    Representa los diferentes tipos de tarifas que se pueden
    aplicar a los productos (ej: Tarifa Normal, Tarifa VIP).

    Campos:
        - name: Nombre de la tarifa
        - created_at: Fecha de creación
    """
    name = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class HourRange(models.Model):
    """
    Modelo de rangos de horas.

    Define las duraciones disponibles para los productos
    (ej: 1 hora, 2 horas, 3 horas).

    Campos:
        - time: Cantidad de horas
    """
    time = models.IntegerField()

    def __str__(self):
        return f"{self.time}h"


class Product(models.Model):
    """
    Modelo de productos del sistema.

    Un producto combina:
    - Tarifa (Rate): Tipo de tarifa aplicable
    - Inmueble (Room): Lugar o ambientes
    - Rango de Horas (HourRange): Duración del producto
    - Días (day): Días de la semana disponibles

    Características:
    - Soft delete: No se elimina físicamente, se marca is_deleted=True
    - Ordering: Ordenado por ID de forma ascendente

    Campos:
        - rate: Referencia a la tarifa
        - room: Referencia al inmueble
        - hour_range: Referencia al rango de horas
        - day: Array de días de la semana (ej: ["lunes", "martes"])
        - is_deleted: Indica si está eliminado (soft delete)
        - created_at: Fecha de creación
        - updated_at: Fecha de última actualización
    """
    rate = models.ForeignKey(Rate, on_delete=models.PROTECT)
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    hour_range = models.ForeignKey(HourRange, on_delete=models.PROTECT)
    day = ArrayField(models.CharField(max_length=255))
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.rate} - {self.room} - {self.hour_range}"

    class Meta:
        ordering = ['id']
        indexes = [
            models.Index(fields=['rate', 'room', 'is_deleted']),
            models.Index(fields=['room', 'is_deleted']),
        ]


class Price(models.Model):
    """
    Modelo de precios e historial de precios.

    Cada producto puede tener múltiples precios a lo largo del tiempo.
    Este modelo mantiene un historial completo de cambios de precio.

    Flujo de cambio de precio:
    1. Se desactiva el precio actual (is_active=False, valid_to=now)
    2. Se crea un nuevo precio (is_active=True, valid_from=now)

    Estados de un precio:
    - Precio activo (is_active=True, valid_to=null): Precio vigente
    - Precio inactivo (is_active=False, valid_to=fecha): Precio histórico

    Campos:
        - product: Referencia al producto
        - mount: Monto del precio
        - is_active: Indica si es el precio vigente
        - valid_from: Fecha desde la cual es válido (null = desde creación)
        - valid_to: Fecha hasta la cual fue válido (null = vigente actual)
        - created_at: Fecha de creación del registro

    Ejemplo:
        Producto X tiene precio 100Bs desde 01/01/2026 hasta 15/01/2026
        y precio 120Bs desde 15/01/2026 (vigente).

        Registro 1: mount=100, is_active=False, valid_from=01/01, valid_to=15/01
        Registro 2: mount=120, is_active=True, valid_from=15/01, valid_to=null
    """
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    mount = models.FloatField()
    is_active = models.BooleanField()
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        estado = "vigente" if self.is_active else "inactivo"
        return f"{self.product} - {self.mount}Bs ({estado})"

    class Meta:
        indexes = [
            models.Index(fields=['product', 'is_active']),
        ]


class Price_Additional_Hour(models.Model):
    """
    Modelo de precios por hora adicional.

    Define el costo extra por cada hora adicional fuera del rango
    del producto seleccionado.

    Campos:
        - hourRange: Referencia al rango de horas
        - room: Referencia al inmueble
        - mount: Monto de la hora adicional
        - state: Estado (activo/inactivo)
        - created_at: Fecha de creación
        - updated_at: Fecha de última actualización
    """
    hourRange = models.ForeignKey(HourRange, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    mount = models.FloatField()
    state = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.room} / {self.hourRange} - {self.mount}Bs"