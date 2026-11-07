from django import forms

from pacientes.forms import validar_cedula_ecuatoriana
from .models import Cliente


def validar_cedula_o_ruc(valor):
    """
    Valida una cédula (10 dígitos) o un RUC (13 dígitos) ecuatoriano.

    Alcance de la comprobación:
      - Cédula: completa, incluido el dígito verificador.
      - RUC de persona natural (tercer dígito 0 a 5): completa, porque sus
        primeros 10 dígitos son justamente la cédula del titular.
      - RUC de entidad pública (6) y de sociedad privada (9): solo estructura.
        Su dígito verificador usa módulo 11 con coeficientes que el SRI no
        publica abiertamente, así que no se comprueba: rechazar un RUC válido
        sería peor que aceptar uno con un dígito errado.
    """
    documento = (valor or '').strip()

    if not documento.isdigit():
        raise forms.ValidationError('La cédula o RUC debe contener solo números.')

    if len(documento) == 10:
        return validar_cedula_ecuatoriana(documento)

    if len(documento) != 13:
        raise forms.ValidationError(
            'El documento debe tener 10 dígitos (cédula) o 13 dígitos (RUC).'
        )

    provincia = int(documento[:2])
    if not (1 <= provincia <= 24 or provincia == 30):
        raise forms.ValidationError(
            'Los dos primeros dígitos del RUC no corresponden a una provincia válida.'
        )

    tercer_digito = int(documento[2])

    if tercer_digito <= 5:
        if not documento.endswith('001'):
            raise forms.ValidationError(
                'Un RUC de persona natural debe terminar en 001.'
            )
        try:
            validar_cedula_ecuatoriana(documento[:10])
        except forms.ValidationError:
            raise forms.ValidationError(
                'Los primeros 10 dígitos del RUC no forman una cédula válida.'
            )
        return documento

    if tercer_digito == 6:
        if not documento.endswith('0001'):
            raise forms.ValidationError(
                'Un RUC de entidad pública debe terminar en 0001.'
            )
        return documento

    if tercer_digito == 9:
        if not documento.endswith('001'):
            raise forms.ValidationError(
                'Un RUC de sociedad debe terminar en 001.'
            )
        return documento

    raise forms.ValidationError(
        'El tercer dígito del RUC debe ser 0 a 5 (persona natural), '
        '6 (entidad pública) o 9 (sociedad).'
    )


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['cedula', 'nombre', 'email', 'telefono', 'direccion', 'paciente']
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '13'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'paciente': forms.HiddenInput(),
        }

    def clean_cedula(self):
        documento = validar_cedula_o_ruc(self.cleaned_data['cedula'])

        duplicados = Cliente.all_objects.filter(cedula=documento)
        if self.instance.pk:
            duplicados = duplicados.exclude(pk=self.instance.pk)
        if duplicados.exists():
            raise forms.ValidationError('Esta cédula o RUC ya está registrada.')

        return documento

    def clean_email(self):
        email = self.cleaned_data['email']

        duplicados = Cliente.all_objects.filter(email=email)
        if self.instance.pk:
            duplicados = duplicados.exclude(pk=self.instance.pk)
        if duplicados.exists():
            raise forms.ValidationError('Este email ya está registrado.')

        return email