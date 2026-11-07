from datetime import date, time

from django import forms

from .models import Paciente, Medico, Cita


# Horario de atención del hospital
HORA_APERTURA = time(7, 0)
HORA_CIERRE = time(19, 0)

# Edad máxima admitida al registrar un paciente
EDAD_MAXIMA = 120


def digito_verificador(nueve_digitos):
    """Calcula el décimo dígito de una cédula ecuatoriana (algoritmo módulo 10)."""
    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0
    for digito, coeficiente in zip(nueve_digitos, coeficientes):
        producto = int(digito) * coeficiente
        total += producto - 9 if producto >= 10 else producto
    return (10 - total % 10) % 10


def validar_cedula_ecuatoriana(valor):
    """
    Valida una cédula ecuatoriana y la devuelve limpia.

    Comprueba cuatro cosas:
      1. Que tenga 10 dígitos numéricos.
      2. Que los dos primeros sean una provincia válida (01 a 24, o 30).
      3. Que el tercero sea menor a 6 (persona natural).
      4. Que el décimo dígito coincida con el verificador calculado.
    """
    cedula = (valor or '').strip()

    if not cedula.isdigit() or len(cedula) != 10:
        raise forms.ValidationError('La cédula debe tener exactamente 10 dígitos numéricos.')

    provincia = int(cedula[:2])
    if not (1 <= provincia <= 24 or provincia == 30):
        raise forms.ValidationError(
            'Los dos primeros dígitos no corresponden a una provincia válida (01 a 24, o 30).'
        )

    if int(cedula[2]) > 5:
        raise forms.ValidationError(
            'El tercer dígito debe ser menor a 6 en una cédula de persona natural.'
        )

    if digito_verificador(cedula[:9]) != int(cedula[9]):
        raise forms.ValidationError(
            'La cédula no es válida: el dígito verificador no coincide. Revise los números.'
        )

    return cedula


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = [
            'cedula', 'nombres', 'apellidos', 'fecha_nacimiento',
            'genero', 'direccion', 'telefono', 'correo_electronico',
        ]
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 10}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo_electronico': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_cedula(self):
        return validar_cedula_ecuatoriana(self.cleaned_data['cedula'])

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data['fecha_nacimiento']
        hoy = date.today()

        if fecha > hoy:
            raise forms.ValidationError('La fecha de nacimiento no puede estar en el futuro.')

        if (hoy.year - fecha.year) > EDAD_MAXIMA:
            raise forms.ValidationError(
                f'La fecha de nacimiento no puede ser de hace más de {EDAD_MAXIMA} años.'
            )

        return fecha


class MedicoForm(forms.ModelForm):
    class Meta:
        model = Medico
        fields = [
            'cedula', 'nombres', 'apellidos', 'especialidad',
            'telefono', 'correo_electronico',
        ]
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 10}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'especialidad': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo_electronico': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_cedula(self):
        return validar_cedula_ecuatoriana(self.cleaned_data['cedula'])


class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['paciente', 'medico', 'fecha', 'hora', 'motivo']
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-select'}),
            'medico': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['paciente'].queryset = Paciente.objects.filter(estado=True)
        self.fields['medico'].queryset = Medico.objects.filter(estado=True)

        # Impide elegir una fecha pasada desde el calendario del navegador.
        self.fields['fecha'].widget.attrs['min'] = date.today().isoformat()

    def clean_fecha(self):
        fecha = self.cleaned_data['fecha']

        # Solo se exige en citas nuevas o cuando la fecha cambia, para no
        # bloquear la edición del motivo de una cita ya pasada.
        if not self.instance.pk or 'fecha' in self.changed_data:
            if fecha < date.today():
                raise forms.ValidationError(
                    'No se puede agendar una cita en una fecha que ya pasó.'
                )

        return fecha

    def clean_hora(self):
        hora = self.cleaned_data['hora']

        if hora < HORA_APERTURA or hora > HORA_CIERRE:
            raise forms.ValidationError(
                f'El horario de atención es de {HORA_APERTURA.strftime("%H:%M")} '
                f'a {HORA_CIERRE.strftime("%H:%M")}.'
            )

        return hora

    def clean(self):
        datos = super().clean()
        medico = datos.get('medico')
        fecha = datos.get('fecha')
        hora = datos.get('hora')

        # El modelo ya tiene una restricción única (médico, fecha, hora). Sin esta
        # comprobación, chocar con ella produce un error 500 en lugar de un aviso.
        if medico and fecha and hora:
            ocupadas = Cita.objects.filter(medico=medico, fecha=fecha, hora=hora)

            if self.instance.pk:
                ocupadas = ocupadas.exclude(pk=self.instance.pk)

            if ocupadas.exists():
                raise forms.ValidationError(
                    f'{medico} ya tiene una cita el {fecha.strftime("%d/%m/%Y")} '
                    f'a las {hora.strftime("%H:%M")}. Elija otro horario.'
                )

        return datos