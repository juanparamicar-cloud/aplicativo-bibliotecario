from django import forms
from .models import Resena


class ResenaForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = ["nombre", "correo", "puntuacion", "comentario", "acepta_datos"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "correo": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "usuario@uninpahu.edu.co",
            }),
            "puntuacion": forms.RadioSelect(
                choices=[(i, i) for i in range(1, 6)],
                attrs={"class": "form-check-input"},
            ),
            "comentario": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "acepta_datos": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "nombre": "Nombre",
            "correo": "Correo institucional",
            "puntuacion": "Puntuación",
            "comentario": "Comentario",
            "acepta_datos": "Autorizo el tratamiento de mis datos personales",
        }

    def clean_acepta_datos(self):
        acepta = self.cleaned_data.get("acepta_datos")
        if not acepta:
            raise forms.ValidationError("Debes aceptar el tratamiento de datos.")
        return acepta
