from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.crypto import get_random_string


def generate_referral_code():
    """Generate unique 8-char alphanumeric referral code."""
    return get_random_string(length=8)


def validate_cedula(value):
    """Validate Colombian cedula format (6-10 digits)"""
    if not value.isdigit():
        raise ValidationError('Cedula must contain only digits')
    if len(value) < 6 or len(value) > 10:
        raise ValidationError('Cedula must be between 6 and 10 digits')


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        USER = 'USER', 'Usuario'
        LEADER = 'LEADER', 'Lider'

    cedula = models.CharField(
        max_length=10,
        unique=True,
        validators=[validate_cedula],
        help_text='Colombian cedula (6-10 digits)'
    )
    nombre_completo = models.CharField(
        max_length=200,
        verbose_name='Nombre Completo'
    )
    phone = models.CharField(
        max_length=20,
        verbose_name='Telefono'
    )
    data_policy_accepted = models.BooleanField(
        default=False,
        verbose_name='Acepto la politica de datos'
    )

    referral_code = models.CharField(
        max_length=8,
        unique=True,
        editable=False,
        default=generate_referral_code,
        verbose_name='Codigo de referido'
    )

    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals',
        verbose_name='Referido por'
    )

    referral_goal = models.PositiveIntegerField(
        default=10,
        verbose_name='Meta de referidos'
    )

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Rol',
    )

    def __str__(self):
        return self.username


class CedulaInfo(models.Model):
    """Census/voting information fetched from Registraduria."""

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        PROCESSING = 'PROCESSING', 'Procesando'
        ACTIVE = 'ACTIVE', 'Activo'
        NOT_FOUND = 'NOT_FOUND', 'No encontrado'
        CANCELLED_DECEASED = 'CANCELLED_DECEASED', 'Cancelada - Fallecido'
        CANCELLED_OTHER = 'CANCELLED_OTHER', 'Cancelada - Otro'
        ERROR = 'ERROR', 'Error'
        TIMEOUT = 'TIMEOUT', 'Timeout'
        BLOCKED = 'BLOCKED', 'Bloqueado'

    # Link to user
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cedula_info',
        verbose_name='Usuario',
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Estado',
    )

    # Voting location fields
    departamento = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Departamento',
    )
    municipio = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Municipio',
    )
    puesto = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Puesto de votacion',
    )
    direccion = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Direccion',
    )
    mesa = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Mesa',
    )

    # Cancelled cedula fields
    novedad = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Novedad',
    )
    resolucion = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Resolucion',
    )
    fecha_novedad = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Fecha de novedad',
    )

    # Metadata fields
    fetched_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de consulta',
    )
    error_message = models.TextField(
        blank=True,
        verbose_name='Mensaje de error',
    )
    raw_response = models.TextField(
        blank=True,
        verbose_name='Respuesta cruda',
        help_text='HTML/JSON response from Registraduria for debugging',
    )
    retry_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Intentos',
    )

    class Meta:
        verbose_name = 'Informacion de cedula'
        verbose_name_plural = 'Informacion de cedulas'

    def __str__(self):
        return f"{self.user.cedula} - {self.get_status_display()}"
