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

    def __str__(self):
        return self.username
