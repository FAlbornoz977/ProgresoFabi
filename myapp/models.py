from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

class Post(models.Model):
    titulo = models.CharField(max_length=100)
    contenido = models.TextField()
    lugar = models.CharField(max_length=100)
    fecha_posteado = models.DateTimeField(auto_now_add=True)
    imagen = models.ImageField(upload_to='images/', blank=True, null=True)  # Nuevo campo para la imagen

    def __str__(self):
        return self.titulo

class Comprobante(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='comprobantes/%Y/%m/')
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.file.name} - {self.uploaded_at.strftime("%Y-%m")}'
    

class Recordatorio(models.Model):
    IMPORTANCIA_CHOICES = [
        ('Baja', 'Baja'),
        ('Media', 'Media'),
        ('Alta', 'Alta'),
    ]
    
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha = models.DateField()
    creado_en = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    importancia = models.CharField(max_length=5, choices=IMPORTANCIA_CHOICES, default='Media')  # Campo de importancia

    def __str__(self):
        return f"{self.titulo} ({self.importancia})"
    

import uuid

class CorreoEnviado1(models.Model):
    correo = models.EmailField()
    archivo = models.FileField(upload_to='archivos/')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    abierto = models.BooleanField(default=False)
    descargado = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.correo} - {self.archivo.name}'