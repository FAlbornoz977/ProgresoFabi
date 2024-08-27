from django.shortcuts import render,redirect,get_object_or_404
from .forms import PostForm, ComprobanteForm
from .models import Post, Comprobante,Recordatorio
from django.contrib.auth.decorators import login_required,user_passes_test
import os
from django.conf import settings
from django.http import HttpResponse, Http404
import pandas as pd
from io import BytesIO
from datetime import datetime
from django.utils import timezone
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




#def presupuesto_view(request):

    if request.method == 'POST':
        # Obtener datos del formulario
        nombre_empresa = request.POST['nombre_empresa']
        cliente = request.POST['cliente']
        telefono = request.POST['telefono']
        email = request.POST['email']
        fono = request.POST['fono']
        fecha_actual = datetime.datetime.now().strftime("%d-%m-%Y")

        # Obtener valores y calcular
        dimensiones_largo = float(request.POST['dimensiones_largo'])
        dimensiones_ancho = float(request.POST['dimensiones_ancho'])
        biselado_largo = float(request.POST['biselado_largo'])
        biselado_ancho = float(request.POST['biselado_ancho'])
        grabado_largo = float(request.POST['grabado_largo'])
        grabado_ancho = float(request.POST['grabado_ancho'])
        perforacion_citofonos = int(request.POST['perforacion_citofonos'])
        calados_cilindricos = int(request.POST['calados_cilindricos'])
        pernos_soldados = int(request.POST['pernos_soldados'])
        pulido_botones = float(request.POST['pulido_botones'])
        plegado = int(request.POST['plegado'])
        perforacion_brocas = int(request.POST['perforacion_brocas'])
        calados_rectilinios = int(request.POST['calados_rectilinios'])
        acrilico = int(request.POST['acrilico'])
        placa_grabada = int(request.POST['placa_grabada'])
        rectificacion_medidas = int(request.POST['rectificacion_medidas'])
        calado_triangular = int(request.POST['calado_triangular'])

        # Definir valores constantes
        valores = {
            'PERFORACIONES_BROCAS': 315,
            'CONST_GRABADO_RAS': 3,
            'VALOR_POR_PERNOS_SOLDADO': 1260,
            'VALOR_POR_PERFORACION_CIRCULAR': 6300,
            'VALOR_CALADO_CITOFONO': 19425,
            'BISELADO_EL': 21,
            'ESPESOR_PLANCHA_M2_MM': 2,
            'VALOR_PL_AC_INOX_2MM': 9240,
            'VALOR_PULIDO_MT2': 14610,
            'VALOR_PLEGADO_POR_KILO': 1050,
            'VALOR_POR_CALADO_RECTILINEO': 8400,
            'VALOR_ACRILICO': 6300,
            'VALOR_CALADO_TRIANGULAR': 8400,
            'RECTIFICACION_DE_MEDIDAS': 26250,
            'SERVICIO_GRABADO_LASER': 15750,
        }

        # Calcular subtotal
        subtotal = (
            (dimensiones_largo * dimensiones_ancho * valores['ESPESOR_PLANCHA_M2_MM'] * 8 / 1000000 * valores['VALOR_PL_AC_INOX_2MM']) +
            (biselado_largo * biselado_ancho * valores['BISELADO_EL']) +
            (grabado_largo * grabado_ancho * valores['CONST_GRABADO_RAS']) +
            (perforacion_citofonos * valores['VALOR_POR_PERFORACION_CIRCULAR']) +
            (calados_cilindricos * valores['VALOR_POR_PERFORACION_CIRCULAR']) +
            (pernos_soldados * valores['VALOR_POR_PERNOS_SOLDADO']) +
            (pulido_botones * valores['VALOR_PULIDO_MT2']) +
            (plegado * valores['VALOR_PLEGADO_POR_KILO']) +
            (perforacion_brocas * valores['PERFORACIONES_BROCAS']) +
            (calados_rectilinios * valores['VALOR_POR_CALADO_RECTILINEO']) +
            (acrilico * valores['VALOR_ACRILICO']) +
            (placa_grabada * valores['SERVICIO_GRABADO_LASER']) +
            (rectificacion_medidas * valores['RECTIFICACION_DE_MEDIDAS']) +
            (calado_triangular * valores['VALOR_CALADO_TRIANGULAR'])
        )

        # Agregar 5% y calcular IVA
        subtotal_con_margen = subtotal * 1.05
        iva = subtotal_con_margen * 0.19
        total = subtotal_con_margen + iva

        # Crear DataFrame para generar el Excel
        df = pd.DataFrame({
            'Descripción': [
                'Dimensiones Botoneras', 'Biselado Botonera', 'Grabado de Botoneras', 'Perforación Citofonos',
                'Calados Cilindricos', 'Pernos Soldados', 'Pulido Botonera', 'Plegado', 'Perforación Brocas',
                'Calados Rectilinios', 'Acrílico', 'Placa Grabada', 'Rectificación de Medidas', 'Calado Triangular'
            ],
            'Cantidad': [
                f"{dimensiones_largo}x{dimensiones_ancho}", f"{biselado_largo}x{biselado_ancho}", 
                f"{grabado_largo}x{grabado_ancho}", perforacion_citofonos, calados_cilindricos, pernos_soldados,
                pulido_botones, plegado, perforacion_brocas, calados_rectilinios, acrilico, placa_grabada,
                rectificacion_medidas, calado_triangular
            ],
            'Subtotal': [
                subtotal, '', '', '', '', '', '', '', '', '', '', '', '', ''
            ],
            'IVA': [
                '', '', '', '', '', '', '', '', '', '', '', '', '', iva
            ],
            'Total': [
                '', '', '', '', '', '', '', '', '', '', '', '', '', total
            ]
        })

        # Generar el Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Presupuesto')

        output.seek(0)
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=presupuesto.xlsx'

        return response

    return render(request, 'myapp/plantilla/presupuesto.html')
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
