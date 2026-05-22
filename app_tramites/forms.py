from django import forms
from .models import NodoTramite, Alumno, Carrera, Pension, Beca, Documento, Pago, Docente, Curso, CursoCarrera

class NodoTramiteForm(forms.ModelForm):
    class Meta:
        model = NodoTramite
        fields = ['nombre', 'descripcion', 'padre', 'orden', 'enlace']
        widgets = {
            'nombre':      forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'padre':       forms.Select(attrs={'class': 'form-control'}),
            'orden':       forms.NumberInput(attrs={'class': 'form-control'}),
            'enlace':      forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Ej: /alumnos/'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['padre'].queryset    = NodoTramite.objects.all()
        self.fields['padre'].required    = False
        self.fields['padre'].empty_label = '-- Nodo raíz --'


class AlumnoForm(forms.ModelForm):
    class Meta:
        model  = Alumno
        fields = ['dni','nombre','apellido','carrera','anio','ciclo',
                  'fecha_ingreso','correo_institucional','telefono',
                  'direccion','fecha_nacimiento']
        widgets = {
            'dni':                  forms.TextInput(attrs={'class':'form-control','maxlength':'8'}),
            'nombre':               forms.TextInput(attrs={'class':'form-control'}),
            'apellido':             forms.TextInput(attrs={'class':'form-control'}),
            'carrera':              forms.Select(attrs={'class':'form-control'}),
            'anio':                 forms.Select(attrs={'class':'form-control'}),
            'ciclo':                forms.Select(attrs={'class':'form-control'}),
            'fecha_ingreso':        forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'correo_institucional': forms.EmailInput(attrs={'class':'form-control','placeholder':'alumno@instituto.edu.pe'}),
            'telefono':             forms.TextInput(attrs={'class':'form-control'}),
            'direccion':            forms.TextInput(attrs={'class':'form-control'}),
            'fecha_nacimiento':     forms.DateInput(attrs={'class':'form-control','type':'date'}),
        }


class CarreraForm(forms.ModelForm):
    class Meta:
        model  = Carrera
        fields = ['nombre','codigo','duracion']
        widgets = {
            'nombre':   forms.TextInput(attrs={'class':'form-control'}),
            'codigo':   forms.TextInput(attrs={'class':'form-control'}),
            'duracion': forms.Select(attrs={'class':'form-control'}),
        }


class PensionForm(forms.ModelForm):
    class Meta:
        model  = Pension
        fields = ['mes','anio','monto','estado','fecha_pago','observacion']
        widgets = {
            'mes':        forms.Select(attrs={'class':'form-control'}),
            'anio':       forms.NumberInput(attrs={'class':'form-control'}),
            'monto':      forms.NumberInput(attrs={'class':'form-control','step':'0.01'}),
            'estado':     forms.Select(attrs={'class':'form-control'}),
            'fecha_pago': forms.DateInput(attrs={'class':'form-control','type':'date'},format='%Y-%m-%d'),
            'observacion':forms.Textarea(attrs={'class':'form-control','rows':3}),
        }


class BecaForm(forms.ModelForm):
    class Meta:
        model  = Beca
        fields = ['tipo','porcentaje','estado','fecha_inicio','fecha_fin','observacion']
        widgets = {
            'tipo':        forms.Select(attrs={'class':'form-control'}),
            'porcentaje':  forms.NumberInput(attrs={'class':'form-control'}),
            'estado':      forms.Select(attrs={'class':'form-control'}),
            'fecha_inicio':forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'fecha_fin':   forms.DateInput(attrs={'class':'form-control','type':'date'},format='%Y-%m-%d'),
            'observacion': forms.Textarea(attrs={'class':'form-control','rows':3}),
        }


class DocumentoForm(forms.ModelForm):
    class Meta:
        model  = Documento
        fields = ['tipo','estado','fecha_entrega','observacion']
        widgets = {
            'tipo':          forms.Select(attrs={'class':'form-control'}),
            'estado':        forms.Select(attrs={'class':'form-control'}),
            'fecha_entrega': forms.DateInput(attrs={'class':'form-control','type':'date'},format='%Y-%m-%d'),
            'observacion':   forms.Textarea(attrs={'class':'form-control','rows':3}),
        }


class PagoForm(forms.ModelForm):
    class Meta:
        model  = Pago
        fields = ['tipo','concepto','monto','metodo','estado','fecha','num_operacion','observacion']
        widgets = {
            'tipo':          forms.Select(attrs={'class':'form-control'}),
            'concepto':      forms.TextInput(attrs={'class':'form-control'}),
            'monto':         forms.NumberInput(attrs={'class':'form-control','step':'0.01'}),
            'metodo':        forms.Select(attrs={'class':'form-control'}),
            'estado':        forms.Select(attrs={'class':'form-control'}),
            'fecha':         forms.DateInput(attrs={'class':'form-control','type':'date'},format='%Y-%m-%d'),
            'num_operacion': forms.TextInput(attrs={'class':'form-control','placeholder':'Opcional'}),
            'observacion':   forms.Textarea(attrs={'class':'form-control','rows':3}),
        }


class DocenteForm(forms.ModelForm):
    class Meta:
        model  = Docente
        fields = ['dni','nombre','apellido','especialidad',
                  'correo_institucional','telefono','fecha_ingreso','activo']
        widgets = {
            'dni':                  forms.TextInput(attrs={'class':'form-control','maxlength':'8'}),
            'nombre':               forms.TextInput(attrs={'class':'form-control'}),
            'apellido':             forms.TextInput(attrs={'class':'form-control'}),
            'especialidad':         forms.Select(attrs={'class':'form-control'}),
            'correo_institucional': forms.EmailInput(attrs={'class':'form-control','placeholder':'docente@instituto.edu.pe'}),
            'telefono':             forms.TextInput(attrs={'class':'form-control'}),
            'fecha_ingreso':        forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'activo':               forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }


class CursoCarreraForm(forms.ModelForm):
    """Asignar/editar un curso dentro de la malla de una carrera."""
    class Meta:
        model  = CursoCarrera
        fields = ['curso','ciclo','docente']
        widgets = {
            'curso':   forms.Select(attrs={'class':'form-control'}),
            'ciclo':   forms.Select(attrs={'class':'form-control'}),
            'docente': forms.Select(attrs={'class':'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['docente'].required    = False
        self.fields['docente'].empty_label = '— Sin asignar —'
        self.fields['docente'].queryset    = Docente.objects.filter(activo=True).order_by('apellido')


class AsignarDocenteForm(forms.ModelForm):
    """Solo para reasignar el docente de un CursoCarrera ya existente."""
    class Meta:
        model  = CursoCarrera
        fields = ['docente']
        widgets = {
            'docente': forms.Select(attrs={'class':'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['docente'].required    = False
        self.fields['docente'].empty_label = '— Sin asignar —'
        self.fields['docente'].queryset    = Docente.objects.filter(activo=True).order_by('apellido')
