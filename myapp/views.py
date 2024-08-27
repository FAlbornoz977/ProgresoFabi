from django.shortcuts import render,redirect,get_object_or_404
from .forms import PostForm, ComprobanteForm, ArchivoForm
from .models import Post, Comprobante,Recordatorio
from django.contrib.auth.decorators import login_required,user_passes_test
import os
from django.conf import settings
from django.http import HttpResponse, Http404
import pandas as pd
from io import BytesIO
from datetime import datetime
from django.utils import timezone
from django.urls import reverse
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.core.mail import EmailMessage
import logging
# views.py

# Verifica si el usuario es de Gerencia o Admin
def user_is_superuser_or_gerencia(user):
    return user.is_superuser or user.groups.filter(name='gerencia').exists()

@login_required
def upload_comprobante(request):
    if user_is_superuser_or_gerencia(request.user):
        if request.method == 'POST':
            form = ComprobanteForm(request.POST, request.FILES)
            if form.is_valid():
                comprobante = form.save(commit=False)
                comprobante.user = request.user
                comprobante.save()
                return redirect('list_comprobantes')
        else:
            form = ComprobanteForm()
        
        return render(request, 'myapp/comprobantes/upload_comprobante.html', {'form': form})
    else:
        return HttpResponse("No tienes permiso para acceder a esta página", status=403)

@login_required
def list_comprobantes(request):
    if user_is_superuser_or_gerencia(request.user):
        # Obtener el año y el mes del request, si están presentes
        year = request.GET.get('year')
        month = request.GET.get('month')
        
        # Filtrar los comprobantes basados en el año y mes proporcionados
        if year and month:
            try:
                year = int(year)
                month = int(month)
                comprobantes = Comprobante.objects.filter(
                    uploaded_at__year=year,
                    uploaded_at__month=month
                )
            except ValueError:
                comprobantes = Comprobante.objects.none()
        else:
            comprobantes = Comprobante.objects.all()
        
        # Obtener los años y meses disponibles para el filtro
        years = Comprobante.objects.dates('uploaded_at', 'year').reverse()
        months = Comprobante.objects.dates('uploaded_at', 'month').distinct()

        return render(request, 'myapp/comprobantes/list_comprobantes.html', {
            'comprobantes': comprobantes,
            'years': years,
            'months': months
        })
    else:
        return HttpResponse("No tienes permiso para acceder a esta página", status=403)

@login_required
def download_comprobante(request, pk):
    if user_is_superuser_or_gerencia(request.user):
        try:
            comprobante = Comprobante.objects.get(pk=pk)
            file_path = os.path.join(settings.MEDIA_ROOT, comprobante.file.name)
            
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{comprobante.file.name}"'
                return response
        except Comprobante.DoesNotExist:
            raise Http404("El archivo no existe")
    else:
        return HttpResponse("No tienes permiso para acceder a esta página", status=403)


@login_required
def lista_recordatorios(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        fecha = request.POST.get('fecha')
        importancia = request.POST.get('importancia')  # Obtén el nivel de importancia del formulario
        
        nuevo_recordatorio = Recordatorio(
            titulo=titulo, 
            descripcion=descripcion, 
            fecha=fecha, 
            usuario=request.user,
            importancia=importancia  # Guarda el nivel de importancia
        )
        nuevo_recordatorio.save()
        
        return redirect('lista_recordatorios')

    recordatorios = Recordatorio.objects.filter(fecha__gte=timezone.now()).order_by('fecha')
    return render(request, 'myapp/recordatorios/lista_recordatorios.html', {'recordatorios': recordatorios})

@login_required
def eliminar_recordatorio(request, id):
    recordatorio = Recordatorio.objects.get(id=id)
    recordatorio.delete()
    return redirect('lista_recordatorios')



#Crear Post
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  # Incluye request.FILES para manejar archivos
        if form.is_valid():
            form.save()
            return redirect('blog')  # Redirige a la página del blog después de guardar
    else:
        form = PostForm()
    return render(request, 'myapp/crear_post.html', {'form': form})
#Editar Post
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog')  # Redirige al blog después de guardar
    else:
        form = PostForm(instance=post)

    return render(request, 'myapp/editar_post.html', {'form': form, 'post': post})
#Eliminar Post
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        post.delete()
        return redirect('blog')  # Redirige al blog después de eliminar

    return render(request, 'myapp/eliminar_post.html', {'post': post})


#vistas de paginas
def home(request):
    return render(request, 'myapp/index.html')

def empresa(request):
    return render(request, 'myapp/Empresa.html')

def trabajos(request):
    return render(request, 'myapp/trabajos.html')

def contacto(request):
    return render(request, 'myapp/contacto.html')

def blog(request):
    posts = Post.objects.all()
    return render(request, 'myapp/blog.html', {'posts': posts})

def page_not_found(request, exception):
    return render(request, 'myapp/error404.html', status=404)

def exito(request):
    return render(request, 'myapp/envio/exito.html')

def error(request):
    return render(request, 'myapp/envio/error.html')

# views.py
# views.py
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from .forms import ArchivoForm
from .models import CorreoEnviado1
import logging

logger = logging.getLogger(__name__)
@login_required
def enviar_archivo(request):
    if request.method == 'POST':
        form = ArchivoForm(request.POST, request.FILES)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            archivo = form.cleaned_data['archivo']

            # Guarda el archivo y el correo en la base de datos
            correo_enviado = CorreoEnviado1(correo=correo, archivo=archivo)
            correo_enviado.save()

            # Crear el cuerpo del correo con solo el enlace de descarga
            subject = 'Archivo Disponible para Descarga'
            body = f'''
                Hemos preparado el archivo solicitado. Puedes descargarlo en el siguiente enlace:
                <a href="http://127.0.0.1:8000/track/download/{correo_enviado.token}">Descargar Archivo</a>
            '''
            email = EmailMessage(
                subject,
                body,
                'prueba.1320@zohomail.com',
                [correo]
            )
            email.content_subtype = "html"  # Si usas HTML

            try:
                email.send()
                return redirect('exito')
            except Exception as e:
                logger.error(f'Error al enviar el correo: {str(e)}')
                return redirect('error')
    else:
        form = ArchivoForm()
    return render(request, 'myapp/envio/enviar_archivo.html', {'form': form})

    
def track_download(request, token):
    try:
        correo_enviado = CorreoEnviado1.objects.get(token=token)
        if not correo_enviado.descargado:
            correo_enviado.descargado = True
            correo_enviado.save()

        response = HttpResponse(correo_enviado.archivo, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{correo_enviado.archivo.name}"'
        return response

    except CorreoEnviado1.DoesNotExist:
        raise Http404("Archivo no encontrado")
    
@login_required

def lista_correos_enviados(request):
    if request.method == 'POST' and 'limpiar_bd' in request.POST:
        CorreoEnviado1.objects.all().delete()
        return redirect('lista_correos_enviados')

    correos_enviados = CorreoEnviado1.objects.all()
    return render(request, 'myapp/envio/lista_correos.html', {'correos_enviados': correos_enviados})