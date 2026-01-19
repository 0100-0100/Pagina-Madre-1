from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


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

    def __str__(self):
        return self.username
