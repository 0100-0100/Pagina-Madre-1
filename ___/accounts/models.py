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

    def is_stale(self, pending_timeout_minutes=2, processing_timeout_minutes=5):
        """
        Check if status is stuck in PENDING or PROCESSING for too long.

        Returns True if the status appears stale (task likely failed to queue
        or worker isn't processing). Used to detect and recover from stuck states.

        Args:
            pending_timeout_minutes: Max time for PENDING status (default 2 min)
            processing_timeout_minutes: Max time for PROCESSING status (default 5 min)
        """
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()

        if self.status == self.Status.PENDING:
            # For PENDING, use user's date_joined as creation proxy
            threshold = self.user.date_joined + timedelta(minutes=pending_timeout_minutes)
            return now > threshold

        if self.status == self.Status.PROCESSING:
            # For PROCESSING, use fetched_at (set when refresh triggered)
            if self.fetched_at:
                threshold = self.fetched_at + timedelta(minutes=processing_timeout_minutes)
                return now > threshold
            else:
                # No fetched_at but PROCESSING - use date_joined as fallback
                threshold = self.user.date_joined + timedelta(minutes=processing_timeout_minutes)
                return now > threshold

        return False

    def reset_if_stale(self):
        """
        Reset status to ERROR if stale, allowing user to retry.

        Returns True if status was reset, False otherwise.
        """
        if self.is_stale():
            self.status = self.Status.ERROR
            self.error_message = 'La verificación tardó demasiado. Por favor, intenta de nuevo.'
            self.save(update_fields=['status', 'error_message'])
            return True
        return False
