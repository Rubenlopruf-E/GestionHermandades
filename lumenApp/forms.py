from datetime import __all__
from django import forms
from .models import *

class HermanoForm(forms.ModelForm):
    class Meta:
        model = Hermano
        fields = ['nombre', 'apellidos', 'dni', 'fecha_nacimiento', 'fecha_ingreso', 'estado', 'imagen']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_nacimiento = cleaned_data.get("fecha_nacimiento")
        fecha_ingreso = cleaned_data.get("fecha_ingreso")

        if fecha_nacimiento and fecha_nacimiento > date.today():
            self.add_error('fecha_nacimiento', "La fecha de nacimiento no puede ser futura.")

        if fecha_ingreso and fecha_nacimiento and fecha_ingreso < fecha_nacimiento:
            self.add_error('fecha_ingreso', "La fecha de ingreso no puede ser anterior a la fecha de nacimiento.")


    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if dni and len(dni) > 9:
            raise forms.ValidationError("El DNI no puede tener más de 9 caracteres.")
        return dni
        

class AsignarRolForm(forms.ModelForm):
    class Meta:
        model = HermanoRol
        fields = ['rol','fecha_inicio', 'fecha_fin']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

class CuotaForm(forms.ModelForm):
    class Meta:
        model = Cuota
        fields = ['importe', 'periodo', 'estado_pago']

class CuotaMasivaForm(forms.Form):
    hermanos = forms.ModelMultipleChoiceField(
        queryset=Hermano.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Selecciona los hermanos"
    )
    importe = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        min_value=0,
        label="Importe de la cuota",
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )
    periodo = forms.ChoiceField(
        choices=PeriodoCuota.choices,
        label="Período"
    )
    estado_pago = forms.ChoiceField(
        choices=EstadoPago.choices,
        label="Estado del pago",
        initial=EstadoPago.PENDIENTE
    )

class CultoForm(forms.ModelForm):
    class Meta:
        model = Culto
        fields = ['tipo', 'fecha_inicio','fecha_fin', 'descripcion',]

        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

class RegistroHermanoForm(forms.ModelForm):
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput,
        required=True
    )
    password2 = forms.CharField(
        label="Repetir Contraseña",
        widget=forms.PasswordInput,
        required=True
    )

    class Meta:
        model = Hermano
        fields = ['nombre', 'apellidos', 'dni', 'fecha_nacimiento','imagen']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")
        dni = cleaned_data.get("dni")

        if password and password2 and password != password2:
            raise ValidationError("Las contraseñas no coinciden.")

        if dni and User.objects.filter(username=dni).exists():
            raise ValidationError("Ya existe un usuario con este DNI.")

        fecha_nacimiento = cleaned_data.get("fecha_nacimiento")

        if fecha_nacimiento and fecha_nacimiento > date.today():
            self.add_error('fecha_nacimiento', "La fecha de nacimiento no puede ser futura.")

       