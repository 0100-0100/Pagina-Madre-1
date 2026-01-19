import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import CustomUser


class ProfileForm(forms.ModelForm):
    """Profile editing form with Bootstrap 5 styling"""

    class Meta:
        model = CustomUser
        fields = ('nombre_completo', 'phone', 'referral_goal')
        widgets = {
            'nombre_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo',
                'maxlength': '60',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numero de telefono',
                'maxlength': '10',
                'inputmode': 'numeric',
            }),
            'referral_goal': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
            }),
        }
        labels = {
            'nombre_completo': 'Nombre Completo',
            'phone': 'Telefono',
            'referral_goal': 'Meta de Referidos',
        }

    def clean_nombre_completo(self):
        """Validate nombre_completo: letters, spaces, accents only, 2-60 chars"""
        nombre = self.cleaned_data.get('nombre_completo', '')
        # Allow letters (including Spanish accented), spaces, hyphens, apostrophes
        if not re.match(r'^[a-zA-ZáéíóúñüÁÉÍÓÚÑÜ\s\'-]+$', nombre):
            raise ValidationError('El nombre solo puede contener letras y espacios')
        if len(nombre) < 2:
            raise ValidationError('El nombre debe tener al menos 2 caracteres')
        if len(nombre) > 60:
            raise ValidationError('El nombre no puede exceder 60 caracteres')
        return nombre

    def clean_phone(self):
        """Validate phone: 10 digits only"""
        phone = self.cleaned_data.get('phone', '')
        if not phone.isdigit() or len(phone) != 10:
            raise ValidationError('El telefono debe tener 10 digitos')
        return phone

    def clean_referral_goal(self):
        """Validate referral_goal: must be >= 0"""
        goal = self.cleaned_data.get('referral_goal', 0)
        if goal < 0:
            raise ValidationError('La meta debe ser mayor o igual a 0')
        return goal


class LoginForm(AuthenticationForm):
    """Login form with Bootstrap 5 styling"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to username field
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ingrese su cédula'
        })
        self.fields['username'].label = 'Cédula'

        # Add Bootstrap classes to password field
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña'
        })
        self.fields['password'].label = 'Contraseña'


class CustomUserCreationForm(UserCreationForm):
    """Registration form with custom fields, validation, and Bootstrap 5 styling"""

    class Meta:
        model = CustomUser
        fields = ('cedula', 'nombre_completo', 'phone', 'password1', 'password2', 'data_policy_accepted')
        widgets = {
            'nombre_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo'
            }),
            'cedula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de cédula',
                'maxlength': '10',
                'inputmode': 'numeric',
                'pattern': '[0-9]{6,10}'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de teléfono',
                'inputmode': 'numeric'
            }),
            'data_policy_accepted': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'nombre_completo': 'Nombre Completo',
            'cedula': 'Cédula',
            'phone': 'Teléfono',
            'data_policy_accepted': 'Acepto la política de datos',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style inherited password fields (Meta.widgets doesn't affect inherited fields)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar Contraseña'

    def clean_nombre_completo(self):
        """Validate nombre_completo: letters, spaces, accents only, max 60 chars"""
        nombre = self.cleaned_data.get('nombre_completo', '')
        # Allow letters (including Spanish accented), spaces, hyphens, apostrophes
        if not re.match(r'^[a-zA-ZáéíóúñüÁÉÍÓÚÑÜ\s\'-]+$', nombre):
            raise ValidationError('El nombre solo puede contener letras y espacios')
        if len(nombre) < 2:
            raise ValidationError('El nombre debe tener al menos 2 caracteres')
        if len(nombre) > 60:
            raise ValidationError('El nombre no puede exceder 60 caracteres')
        return nombre

    def clean_data_policy_accepted(self):
        """Validate that user accepted the data policy"""
        accepted = self.cleaned_data.get('data_policy_accepted')
        if not accepted:
            raise ValidationError('Debe aceptar la política de datos para registrarse')
        return accepted

    def save(self, commit=True):
        """Set username to cedula before saving"""
        user = super().save(commit=False)
        user.username = self.cleaned_data['cedula']
        if commit:
            user.save()
        return user
