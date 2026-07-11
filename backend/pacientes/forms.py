from datetime import date

from django import forms
from .models import Paciente, Cita, Medico


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


class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ["paciente", "medico", "fecha", "hora", "motivo"]
        widgets = {
            "paciente": forms.Select(attrs={"class": "form-select"}),
            "medico": forms.Select(attrs={"class": "form-select"}),
            "fecha": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "hora": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "motivo": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        medico = cleaned_data.get("medico")
        fecha = cleaned_data.get("fecha")
        hora = cleaned_data.get("hora")

        if medico and fecha and hora:
            conflicto = Cita.objects.filter(
                medico=medico, fecha=fecha, hora=hora
            ).exclude(pk=self.instance.pk)
            if conflicto.exists():
                raise forms.ValidationError(
                    "Ese médico ya tiene una cita agendada en esa fecha y hora."
                )

        if fecha and fecha < date.today():
            raise forms.ValidationError("No se pueden agendar citas en fechas pasadas.")

        return cleaned_data


class MedicoForm(forms.ModelForm):
    class Meta:
        model = Medico
        fields = [
            "cedula",
            "nombres",
            "apellidos",
            "especialidad",
            "telefono",
            "correo_electronico",
        ]
        widgets = {
            "cedula": forms.TextInput(attrs={"class": "form-control", "maxlength": 10}),
            "nombres": forms.TextInput(attrs={"class": "form-control"}),
            "apellidos": forms.TextInput(attrs={"class": "form-control"}),
            "especialidad": forms.Select(attrs={"class": "form-select"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "correo_electronico": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean_cedula(self):
        cedula = self.cleaned_data["cedula"]
        if not cedula.isdigit() or len(cedula) != 10:
            raise forms.ValidationError("La cédula debe tener exactamente 10 dígitos numéricos.")
        return cedula