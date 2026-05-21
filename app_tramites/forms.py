from django import forms
from .models import Alumno, Carrera, Pension, Beca, Documento

class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumno
        fields = ['dni', 'nombre', 'apellido', 'carrera', 'anio', 'ciclo', 'fecha_ingreso']
        widgets = {
            'dni': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '8'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'carrera': forms.Select(attrs={'class': 'form-control'}),
            'anio': forms.Select(attrs={'class': 'form-control'}),
            'ciclo': forms.Select(attrs={'class': 'form-control'}),
            'fecha_ingreso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class CarreraForm(forms.ModelForm):
    class Meta:
        model = Carrera
        fields = ['nombre', 'codigo', 'duracion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'duracion': forms.Select(attrs={'class': 'form-control'}),
        }

class PensionForm(forms.ModelForm):
    class Meta:
        model = Pension
        fields = ['mes', 'anio', 'monto', 'estado', 'fecha_pago', 'observacion']
        widgets = {
            'mes': forms.Select(attrs={'class': 'form-control'}),
            'anio': forms.NumberInput(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'fecha_pago': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class BecaForm(forms.ModelForm):
    class Meta:
        model = Beca
        fields = ['tipo', 'porcentaje', 'estado', 'fecha_inicio', 'fecha_fin', 'observacion']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'porcentaje': forms.NumberInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['tipo', 'estado', 'fecha_entrega', 'observacion']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'fecha_entrega': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
