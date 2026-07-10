from django import forms
from .models import Paciente


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = [
            "cedula",
            "nombres",
            "apellidos",
            "fecha_nacimiento",
            "genero",
            "direccion",
            "telefono",
            "correo_electronico",
        ]
        widgets = {
            "cedula": forms.TextInput(attrs={"class": "form-control", "maxlength": 10}),
            "nombres": forms.TextInput(attrs={"class": "form-control"}),
            "apellidos": forms.TextInput(attrs={"class": "form-control"}),
            "fecha_nacimiento": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "genero": forms.Select(attrs={"class": "form-select"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "correo_electronico": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean_cedula(self):
        cedula = self.cleaned_data["cedula"]
        if not cedula.isdigit() or len(cedula) != 10:
            raise forms.ValidationError("La cédula debe tener exactamente 10 dígitos numéricos.")
        return cedula