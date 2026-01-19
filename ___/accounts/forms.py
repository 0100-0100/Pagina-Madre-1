from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import CustomUser


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
    """Registration form with custom fields and validation"""

    class Meta:
        model = CustomUser
        fields = ('password1', 'password2', 'nombre_completo', 'cedula', 'phone', 'data_policy_accepted')

    def clean_data_policy_accepted(self):
        """Validate that user accepted the data policy"""
        accepted = self.cleaned_data.get('data_policy_accepted')
        if not accepted:
            raise ValidationError('You must accept the data policy to register')
        return accepted

    def save(self, commit=True):
        """Set username to cedula before saving"""
        user = super().save(commit=False)
        user.username = self.cleaned_data['cedula']
        if commit:
            user.save()
        return user
