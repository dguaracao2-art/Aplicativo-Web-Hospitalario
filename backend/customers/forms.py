from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):

    class Meta:
        model = Cliente
        fields = [
            'cedula',
            'nombres',
            'apellidos',
            'fecha_nacimiento',
            'sexo',
            'telefono',
            'email',
            'direccion',
            'foto'
        ]

        widgets = {
            'cedula': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '10'
            }),

            'nombres': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'apellidos': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),

            'sexo': forms.Select(attrs={
                'class': 'form-select'
            }),

            'telefono': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),

            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),

            'foto': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }

    def clean_cedula(self):
        cedula = self.cleaned_data['cedula']

        qs = Cliente.all_objects.filter(cedula=cedula)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError(
                "Esta cédula ya está registrada."
            )

        return cedula

    def clean_email(self):
        email = self.cleaned_data['email']

        if email:
            qs = Cliente.all_objects.filter(email=email)

            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise forms.ValidationError(
                    "Este correo electrónico ya está registrado."
                )

        return email