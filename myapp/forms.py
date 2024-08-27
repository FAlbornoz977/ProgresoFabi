# forms.py
from django import forms
from .models import Post
from .models import Comprobante

class ComprobanteForm(forms.ModelForm):
    class Meta:
        model = Comprobante
        fields = ['file']


        
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['titulo', 'contenido', 'lugar', 'imagen']  # Incluye el campo de imagen


class ArchivoForm(forms.Form):
    correo = forms.EmailField(label='Correo del Cliente')
    archivo = forms.FileField(label='Archivo')