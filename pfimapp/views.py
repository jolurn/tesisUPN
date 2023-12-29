from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import  AuthenticationForm
from pfimapp.models import Curso,Docente,Periodo,DetalleMatricula,ReporteEconomico,ReporteEcoConceptoPago,CustomUser,Matricula,DetalleMatricula,Alumno,Sede,Maestria,TipoDocumento,EstadoCivil

from django.contrib.auth import login, logout, authenticate
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from pfimapp.forms import CustomUserCreationForm,CustomUserForm
from django.views.generic import UpdateView
from .forms import CustomAuthenticationForm
from django.contrib.auth.views import LoginView
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView

from django.http import HttpResponse
import os 
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from datetime import datetime
from PIL import Image
from django.templatetags.static import static
from django.conf import settings

from django.contrib.auth.mixins import LoginRequiredMixin


from django.http import JsonResponse


from django.contrib.admin.views.decorators import staff_member_required

from django.http import JsonResponse

import re
from django.db.models import F

from django.contrib import messages

def extract_year_period(period_code):
    match = re.search(r'(\d{4})-(\d)-', period_code)    
    if match:
        year = int(match.group(1))
        period = int(match.group(2))
        return year, period
    return 0, 0

def orden_periodo(period_code):
    year, period = extract_year_period(period_code)
    return (year, period, period_code)

@login_required
def obtener_alumnos_por_periodo(request):
    periodo_id = request.GET.get('periodo_id')
    alumnos = Alumno.objects.filter(matricula__seccion__periodo_id=periodo_id, estado="A").order_by('usuario__apellidoPaterno').distinct()
    
    alumnos_list = [{'id': alumno.id, 'nombre_completo': alumno.usuario.nombre_completos().upper()} for alumno in alumnos]
    
    return JsonResponse({'alumnos': alumnos_list})

@login_required
def obtener_alumnos_por_sede(request):
    sede_id = request.GET.get('sede_id')
    alumnos = Alumno.objects.filter(sede_id=sede_id, estado="A").order_by('usuario__apellidoPaterno')
    alumnos_list = [{'id': alumno.id, 'nombre_completo': alumno.usuario.nombre_completos().upper()} for alumno in alumnos]
    return JsonResponse({'alumnos': alumnos_list})

# @staff_member_required
def admin_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            error_message = 'Correo electrónico o contraseña incorrectos'
    else:
        error_message = ''

    return render(request, 'admin_login.html', {'error_message': error_message})

def docente_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            try:
                docentes = Docente.objects.filter(usuario=user).first()
                # Si el usuario autenticado es un docente, permitir el inicio de sesión
                login(request, user)
                # Redirigir a la página para seleccionar opciones antes de cargar calificaciones
                return redirect('cargar_calificaciones')
            except Docente.DoesNotExist:
                error_message = 'Usuario no autorizado para ingresar calificaciones.'
        else:
            error_message = 'Correo electrónico o contraseña incorrectos'
    else:
        error_message = ''

    return render(request, 'docente_login.html', {'error_message': error_message})

from django.db.models import Count
@staff_member_required
def cargar_calificaciones(request):
    usuario_docente = request.user

    try:
        # Obtener el docente relacionado con el usuario
        docente = Docente.objects.filter(usuario=usuario_docente).first()

        # Obtener las secciones relacionadas con el docente
        secciones_docente = Seccion.objects.filter(docente=docente)

        # Obtener los periodos a partir de las secciones
        periodos = Periodo.objects.filter(id__in=secciones_docente.values('periodo'))

        # Filtrar los periodos para incluir solo aquellos con al menos un alumno matriculado
        periodos_con_alumnos = periodos.annotate(num_matriculados=Count('seccion__matricula__alumno')).filter(num_matriculados__gt=0)

        context = {'periodos': periodos_con_alumnos}

        return render(request, 'carga_calificaciones.html', context)

    except Docente.DoesNotExist:
        # Manejar el caso en que el usuario no esté asociado a un docente
        # Puedes redirigir a una página de error o hacer lo que sea necesario
        return render(request, 'error.html')

def obtener_maestrias_y_cursos(request):
    if request.method == 'GET':
        periodo_id = request.GET.get('periodo_id')

        # Obtener el usuario del docente que hizo login
        usuario_docente = request.user

        try:
            # Obtener el docente relacionado con el usuario
            # docente = Docente.objects.filter(usuario=usuario_docente)
            
            # Obtener las secciones relacionadas con el docente para el periodo seleccionado
            secciones = Seccion.objects.filter(
                docente__usuario=usuario_docente,
                periodo__id=periodo_id
            ).distinct()

            # Obtener maestrías y cursos de las secciones sin duplicados y con alumnos matriculados
            maestrias_set = set()
            cursos_set = set()

            for seccion in secciones:
                num_alumnos_matriculados = Matricula.objects.filter(seccion=seccion).count()

                if num_alumnos_matriculados > 0:
                    maestrias_set.add((seccion.maestria.id, seccion.maestria.nombre))
                    cursos_set.add((seccion.curso.id, seccion.curso.nombre))

            # Convertir los conjuntos a listas
            maestrias = [{'id': id, 'nombre': nombre} for id, nombre in maestrias_set]
            cursos = [{'id': id, 'nombre': nombre} for id, nombre in cursos_set]

            response_data = {'maestrias': maestrias, 'cursos': cursos}
            return JsonResponse(response_data)

        except Docente.DoesNotExist:
            return JsonResponse({'error': 'Docente no encontrado'})

    else:
        return JsonResponse({'error': 'Método no permitido'})

@staff_member_required
def admin_dashboard(request):
    # Lógica de la página principal del panel de administración
    # Aquí puedes realizar consultas a la base de datos, procesar datos, etc.

    context = {
        # Agrega aquí los datos que deseas pasar al template
        # Por ejemplo:
        'title': 'Panel de Administración',
        'message': 'Bienvenido al panel de administración',
    }

    return render(request, 'admin_dashboard.html', context)

@login_required
def generar_reporte_boleta_matricula(request):
    # Obtener todos los periodos asociados a las matrículas existentes
    periodos = Periodo.objects.filter(seccion__matricula__isnull=False).distinct()

    alumnos = Alumno.objects.all()
    
    periodo_id = request.POST.get('periodo_matricula')
    alumno_id = request.POST.get('alumno_matricula')
    
    detalleAcademico = DetalleMatricula.objects.none()  # Crear un queryset vacío
    
    if periodo_id or alumno_id:
        # Aplicar los filtros solo si se proporciona al menos uno de los parámetros
        detalleAcademico = DetalleMatricula.objects.all()
        
        if periodo_id:
            detalleAcademico = detalleAcademico.filter(matricula__seccion__periodo_id=periodo_id)
            alumnos = alumnos.filter(id=alumno_id, matricula__seccion__periodo_id=periodo_id)
            
        if alumno_id:
            detalleAcademico = detalleAcademico.filter(matricula__alumno_id=alumno_id).distinct()
       
    boletas_disponibles = detalleAcademico.exists()

    #Dividir los nombres de los alumnos por el guion
    alumnos = [alumno.nombre_completo().split('-')[0] for alumno in alumnos]

    contexto = {
        'periodos': periodos,
        'detalleAcademico': detalleAcademico,
        'boletas_disponibles': boletas_disponibles,
        'alumno_nombre': alumnos,
        'periodo_id': periodo_id,
        'alumno_id': alumno_id,
        # Agrega aquí los demás datos necesarios para el template
    }

    return render(request, 'reporte_boleta_matricula.html', contexto)


@login_required
def registro_pagos(request):
    sedes = Sede.objects.all()
    alumnos = Alumno.objects.all()

    sede_id = request.POST.get('sede_pago')
    alumno_id = request.POST.get('alumno_pago')

    detalleDePago = ReporteEcoConceptoPago.objects.none()  # Crear un queryset vacío

    if sede_id or alumno_id:
        # Aplicar los filtros solo si se proporciona al menos uno de los parámetros
        detalleDePago = ReporteEcoConceptoPago.objects.all()

        if sede_id:
            detalleDePago = detalleDePago.filter(reporteEconomico__alumno__sede_id=sede_id)            
            alumnos = alumnos.filter(id=alumno_id, sede_id=sede_id)

        if alumno_id:
            detalleDePago = detalleDePago.filter(reporteEconomico__alumno_id=alumno_id).distinct()

    # Verificar si hay resultados
    resultados_disponibles = detalleDePago.exists()

    usuario_actual = request.user
    alumno_actual = None

    try:
        alumno_actual = Alumno.objects.get(usuario=usuario_actual)
    except Alumno.DoesNotExist:
        pass
    
    #Dividir los nombres de los alumnos por el guion
    alumnos = [alumno.nombre_completo().split('-')[0] for alumno in alumnos]

    return render(request, 'registro_pagos.html', {
        'detalleDePago': detalleDePago,
        'sedes': sedes,
        'alumnos_pagos': alumnos,
        'resultados_disponibles': resultados_disponibles,
        'alumno_actual': alumno_actual,
        'sede_id': sede_id,
        'alumno_id': alumno_id,
    })

@login_required
def reporte_calificaciones(request):
    sedes = Sede.objects.all()
    alumnos = Alumno.objects.all()

    sede_id = request.POST.get('sede')
    alumno_id = request.POST.get('alumno')
       
    detalleAcademico = DetalleMatricula.objects.none()  # Crear un queryset vacío

    if sede_id or alumno_id:
        detalleAcademico = DetalleMatricula.objects.prefetch_related(
        'calificacion_set',
        'matricula__alumno__usuario',
        'seccion__periodo',
        'seccion__maestria',
        'seccion__curso',
        'seccion__docente').filter(calificacion__isnull=False)
        
        if sede_id:
            detalleAcademico = detalleAcademico.filter(matricula__alumno__sede_id=sede_id).order_by(F('seccion__periodo__codigo'))
            alumnos = alumnos.filter(id=alumno_id, sede_id=sede_id)

        if alumno_id:
            detalleAcademico = detalleAcademico.filter(matricula__alumno_id=alumno_id).distinct()

    # Verificar si hay resultados
    resultados_disponibles = detalleAcademico.exists()

    usuario_actual = request.user
    alumno_actual = None

    try:
        alumno_actual = Alumno.objects.get(usuario=usuario_actual)
    except Alumno.DoesNotExist:
        pass

    #Dividir los nombres de los alumnos por el guion
    alumnos = [alumno.nombre_completo().split('-')[0] for alumno in alumnos]

    return render(request, 'reporte_calificaciones.html', {
        'detalleAcademico': detalleAcademico,
        'sedes': sedes,
        'alumnos': alumnos,
        'resultados_disponibles': resultados_disponibles,
        'alumno_actual': alumno_actual,
        'sede_id': sede_id,
        'alumno_id': alumno_id,
    })

def home(request):
    return render(request,'home.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect('reporteEconomico')

    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

@method_decorator(login_required, name='dispatch')
class CustomUserUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    template_name = 'customuser_form.html'
    form_class = CustomUserForm
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        """
        Retorna el objeto CustomUser que se va a editar. Sólo permite editar al usuario autenticado.
        """
        if queryset is None:
            queryset = self.get_queryset()

        pk = self.kwargs.get('pk', None)
        if pk is not None:
            if self.request.user.pk == pk:
                obj = get_object_or_404(queryset, pk=pk)
                return obj

        return self.request.user

@login_required
def reporteEconomico(request):
    try:
        alumno_login = Alumno.objects.get(usuario=request.user, estado="A")                
    except Alumno.DoesNotExist:
        alumno_login = None
    
    reporteEcon = ReporteEconomico.objects.filter(alumno__usuario=request.user, estado="A")
    if reporteEcon:
        detalleRepoEco = ReporteEcoConceptoPago.objects.filter(reporteEconomico=reporteEcon.first(), estado="A")
    else:
        detalleRepoEco = []

    return render(request, 'reporteEconomico.html', {'reporteEconomicos': detalleRepoEco, 'alumno_login': alumno_login})

@login_required
def reporteAcademico(request):
    
    reporteAcad = DetalleMatricula.objects.filter(matricula__alumno__usuario=request.user, estado="A").order_by('seccion__periodo__codigo')
    
    if reporteAcad.exists():
        alumno_login = Alumno.objects.get(usuario=request.user, estado="A")

        reporteEcon = ReporteEconomico.objects.filter(alumno__usuario=request.user, estado="A")
        if reporteEcon.exists():
            detalleRepoEco = ReporteEcoConceptoPago.objects.filter(reporteEconomico=reporteEcon.first(), estado="A")
        else:
            detalleRepoEco = []

        # Comprobar si hay algún registro con el campo 'numeroRecibo' nulo
        hay_registro_nulo = False
        hay_estadoBoletaPag_pendiente = False
        for detalle in detalleRepoEco:
            if detalle.numeroRecibo is None:
                hay_registro_nulo = True
                break
            elif detalle.estadoBoletaPago_id == 2:
                hay_estadoBoletaPag_pendiente = True
                break

        return render(request, 'reporteAcademico.html', {'reporteAcademicos': reporteAcad, 'alumno_login':alumno_login,'reporteEconomicos': detalleRepoEco, 'hay_registro_nulo': hay_registro_nulo, 'hay_estadoBoletaPag_pendiente':hay_estadoBoletaPag_pendiente})
    else:
        return render(request, 'reporteAcademico.html', {'reporteAcademicos': reporteAcad})

@login_required
def reporteMatricula(request):
    try:
        matriculas = DetalleMatricula.objects.filter(matricula__alumno__usuario=request.user, estado="A")
    except DetalleMatricula.DoesNotExist:
        matriculas = []
    
    return render(request, 'matricula.html', {'matriculas': matriculas})


@login_required
def detalleMatricula(request, matricula_id):
    detalleAcademico = DetalleMatricula.objects.filter(matricula=matricula_id)
    alumno_login = Alumno.objects.get(usuario=request.user, estado="A")
    
    if detalleAcademico.exists():
        periodo = detalleAcademico.first().seccion.periodo
    else:
        periodo = None

    return render(request, 'detalleMatricula.html', {'detalleAcademico': detalleAcademico, 'periodo': periodo, 'alumno_login':alumno_login})

@login_required
def signout(request):
    logout(request)
    return redirect('home')

class CustomLoginView(LoginView):
    template_name = 'signin.html'
    form_class = CustomAuthenticationForm
    success_url = '/'

class CustomPasswordChangeView(PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('home')
    template_name = 'change_password.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Contraseña cambiada exitosamente.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Hubo un problema al cambiar la contraseña. Su contraseña no puede ser demasiado similar a su otra información personal. Su contraseña debe contener al menos 8 caracteres. Su contraseña no puede ser una contraseña de uso común. Su contraseña no puede ser completamente numérica.')
        return super().form_invalid(form)

    def dispatch(self, request, *args, **kwargs):
        # Aquí también podrías agregar lógica personalizada si es necesario
        return super().dispatch(request, *args, **kwargs)

@login_required
def generar_pdf(request):
    image_path = os.path.join(settings.STATICFILES_DIRS[0], 'pfimapp/img/logo.png')
    logo = Image.open(image_path)

    detalleAcademico = DetalleMatricula.objects.filter(matricula__alumno__usuario=request.user, estado="A").order_by('seccion__periodo__codigo')
           
    #Create the HttpResponse headers with PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=PosgradoFIM-student-report.pdf'
    # Create the PDF object, using the bytesIO object as its "file."
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    from datetime import datetime

    # Draw the image in the header
    logo_width, logo_height = logo.size
    aspect_ratio = logo_height / logo_width
    logo_width = 250
    logo_height = logo_width * aspect_ratio
    logo_url = request.build_absolute_uri(static('pfimapp/img/logo.png'))
    c.drawImage(logo_url, 170, 730, width=logo_width, height=logo_height)

    c.setFont('Helvetica',12)
    user_name = request.user.nombre_completos()
    c.drawString(30, 705, f'ALUMNO: {user_name}')    
     
    # Use today() method to get current date
    current_date = datetime.today().strftime('%d/%m/%Y')
    c.drawString(480, 705, current_date)
    # start X, height end y, height
    c.line(460,702,560,702)
  
    #table header
    styles = getSampleStyleSheet()
    styleBH = styles["Normal"]
    styleBH.alignment = TA_CENTER
    styleBH.fontSize = 10
        
    # Table data
    # encabezado de la tabla
    header = ['Periodo', 'Código', 'Curso', 'Crédito']
    primer_detalle = detalleAcademico.first()
    if primer_detalle:
        for calificacion in primer_detalle.calificacion_set.all():
            cadena_minuscula = calificacion.definicionCalificacion.nombre.lower()
            header.append(cadena_minuscula.capitalize())
        header += ['Retirado']

    data = [header, ]
    high = 650
    for detalle in detalleAcademico:
        student = [
            str(detalle.seccion.periodo.codigo),
            str(detalle.seccion.curso.codigo),
            str(detalle.seccion.curso.nombre),
            str(detalle.seccion.curso.credito),
            
        ]
        # Agregar valores de calificaciones dinámicas
        for calificacion in detalle.calificacion_set.all():
            student.append(str(calificacion.nota))

        student += ['Si' if detalle.retirado else 'NO']

        data.append(student)
        high = high - 18

    width, height = A4
    table = Table(data, colWidths=[1.2 * cm, 0.9 * cm, 9.1 * cm,  0.9 * cm] + [1 * cm] * len(header[5:-2]) + [1.9 * cm, 1.2 * cm])
    table.setStyle(TableStyle([
    # Estilo de las celdas de la tabla
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Estilo de fuente
        ('FONTSIZE', (0, 0), (-1, -1), 7.2),  # Tamaño de fuente
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Color de fondo de la fila del encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Color de texto de la fila del encabezado
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Alineación del texto en la fila del encabezado
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Estilo de fuente
        ('FONTSIZE', (0, 1), (-1, -1), 4.5),  # Tamaño de fuente
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alineación del texto en todas las celdas
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alineación vertical del texto en todas las celdas
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),  # Estilo de las líneas de la tabla
    ]))
    # pdf size
    table.wrapOn(c, width, height)
    table.drawOn(c, 30, high)
    c.showPage() # save page

    # save pdf
    c.save()
    #get the value of BytesIO buffer and write response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def guardar_calificaciones(request):
    if request.method == 'POST':
        periodo_id = request.POST.get('periodo_id')
        maestria_id = request.POST.get('maestria_id')
        curso_id = request.POST.get('curso_id')        
        
        # Obtener el primer objeto de Seccion en el conjunto de consultas
        docente_seccion = Seccion.objects.filter(
            periodo_id=periodo_id,
            maestria_id=maestria_id,
            curso_id=curso_id
        ).first()

        if docente_seccion:
            # Redireccionar a la vista 'editar_notas' con el ID de la sección
            return redirect('editar_notas', seccion_id=docente_seccion.id)

    # Si el método es GET o no se encontró la sección, mostrar el formulario para ingresar calificaciones
    return render(request, 'editar_notas.html')

from django.shortcuts import render
from .models import Seccion, DetalleMatricula, DefinicionCalificacion, Calificacion

def editar_notas(request, seccion_id):
    
    seccion = Seccion.objects.get(pk=seccion_id)
    alumnos = seccion.matricula_set.all()
    
    definiciones = DefinicionCalificacion.objects.filter(seccion=seccion)

    if request.method == 'POST':
        for alumno in alumnos:
            for definicion in definiciones:
                calificacion, created = Calificacion.objects.get_or_create(
                    detalle_matricula=DetalleMatricula.objects.get(matricula=alumno, seccion=seccion),
                    definicionCalificacion=definicion
                )
                calificacion.nota = request.POST.get(f'alumno_{alumno.id}_definicion_{definicion.id}')
                calificacion.save()

            # Calcular notas finales
            # for alumno in alumnos:
            #     detalle_matricula = DetalleMatricula.objects.get(matricula=alumno, seccion=seccion)
            #     detalle_matricula.calcular_nota_final()
            
    return render(request, 'editar_nota.html', {
        'seccion': seccion,
        'alumnos': alumnos,
        'definiciones': definiciones,
    })

# Esta vista procesará las actualizaciones de calificaciones vía AJAX
def actualizar_calificacion(request):
    if request.method == 'GET':
        # Procesar los valores enviados desde la solicitud GET
        input_name = request.GET.get('input_name')

        # Extraer alumno_id y definicion_id de input_name (debes implementar esta lógica)
        parts = input_name.split('_')
        alumno_id = parts[1]  # Asumiendo que el alumno_id es el segundo componente
        definicion_id = parts[3]  # Asumiendo que el definicion_id es el cuarto componente

        # Buscar todas las calificaciones en la base de datos para el alumno y definición especificados
        calificaciones = Calificacion.objects.filter(
            detalle_matricula__matricula__id=alumno_id,
            definicionCalificacion__id=definicion_id
        )

        # Crear una lista de notas de todas las calificaciones encontradas
        notas = [calificacion.nota for calificacion in calificaciones]        
        return JsonResponse({'mensaje': 'Calificaciones obtenidas exitosamente.', 'notas': notas})

    return JsonResponse({'error': 'Solicitud no válida.'})

# pdf de administrador

@login_required
def generar_pdf_administrativo(request):
    sede_id = request.GET.get('sede')
    alumno_id = request.GET.get('alumno')

    image_path = os.path.join(settings.STATICFILES_DIRS[0], 'pfimapp/img/logo.png')
    logo = Image.open(image_path)

    detalleAcademico = DetalleMatricula.objects.none().order_by('seccion__periodo__codigo')

    detalleAcademico = DetalleMatricula.objects.prefetch_related(
    'calificacion_set',
    'matricula__alumno__usuario',
    'seccion__periodo',
    'seccion__maestria',
    'seccion__curso',
    'seccion__docente').filter(calificacion__isnull=False)

    if sede_id or alumno_id:
        detalleAcademico = detalleAcademico.filter(matricula__alumno__sede_id=sede_id).order_by(F('seccion__periodo__codigo'))

        if alumno_id:
            detalleAcademico = detalleAcademico.filter(matricula__alumno_id=alumno_id).distinct()

    # Crear la respuesta PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=PosgradoFIM-student-report.pdf'

    # Crear el objeto PDF usando el objeto BytesIO como su "archivo".
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Dibujar la imagen en el encabezado
    logo_width, logo_height = logo.size
    aspect_ratio = logo_height / logo_width
    logo_width = 250
    logo_height = logo_width * aspect_ratio
    logo_url = request.build_absolute_uri(static('pfimapp/img/logo.png'))
    c.drawImage(logo_url, 170, 730, width=logo_width, height=logo_height)

    c.setFont('Helvetica', 12)
    c.drawString(30, 905, 'Datos del Reporte Académico')

    c.setFont('Helvetica', 12)
    user_name = detalleAcademico.first().matricula.alumno.nombre_completo()
    user_name = user_name.split('-')[0] 
    c.drawString(30, 705, f'ALUMNO: {user_name.upper()}')

    c.setFont('Helvetica', 10)
    especialidad = detalleAcademico.first().seccion.maestria.nombre
    c.drawString(30, 685, f'ESPECIALIDAD: {especialidad}')

    current_date = datetime.today().strftime('%d/%m/%Y')
    c.drawString(480, 705, current_date)
    c.line(460, 702, 560, 702)

    # Table header
    styles = getSampleStyleSheet()
    styleBH = styles["Normal"]
    styleBH.alignment = TA_CENTER
    styleBH.fontSize = 10

    # Crear encabezado dinámico para las calificaciones
    header = ['Periodo', 'Código', 'Curso', 'Crédito']
    primer_detalle = detalleAcademico.first()
    if primer_detalle:
        for calificacion in primer_detalle.calificacion_set.all():
            cadena_minuscula = calificacion.definicionCalificacion.nombre.lower()
            header.append(cadena_minuscula.capitalize())
        header += ['Retirado']

        data = [header, ]
        high = 650

        for detalle in detalleAcademico:
            periodo_codigo = detalle.seccion.periodo.codigo
            periodo_parte_mostrar = '-'.join(periodo_codigo.split(' ')[0].split('-')[:3])

            # Crear fila de datos dinámicos
            student = [
                str(periodo_parte_mostrar),
                str(detalle.seccion.curso.codigo),
                str(detalle.seccion.curso.nombre),
                str(detalle.seccion.curso.credito),                
            ]

            # Agregar valores de calificaciones dinámicas
            for calificacion in detalle.calificacion_set.all():
                student.append(str(calificacion.nota))

            student += ['Si' if detalle.retirado else 'NO']

            data.append(student)
            high = high - 18

        width, height = A4
        table = Table(data, colWidths=[1.2 * cm, 0.9 * cm, 9.1 * cm,  0.9 * cm] + [1 * cm] * len(header[5:-2]) + [1.9 * cm, 1.2 * cm])

        table.setStyle(TableStyle([
            # Estilo de las celdas de la tabla
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Estilo de fuente
            ('FONTSIZE', (0, 0), (-1, -1), 7.2),  # Tamaño de fuente
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Color de fondo de la fila del encabezado
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Color de texto de la fila del encabezado
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Alineación del texto en la fila del encabezado
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Estilo de fuente
            ('FONTSIZE', (0, 1), (-1, -1), 5),  # Tamaño de fuente
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alineación del texto en todas las celdas
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alineación vertical del texto en todas las celdas
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),  # Estilo de las líneas de la tabla
        ]))

        # pdf size
        table.wrapOn(c, width, height)
        table.drawOn(c, 30, high)
        c.showPage()

        # save pdf
        c.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse

@login_required
def generar_pdf_pagos(request):
    sede_id = request.GET.get('sede')
    alumno_id = request.GET.get('alumno')
    
    image_path = os.path.join(settings.STATICFILES_DIRS[0], 'pfimapp/img/logo.png')
    logo = Image.open(image_path)

    detalleDePago = ReporteEcoConceptoPago.objects.none()  # Crear un queryset vacío

    if sede_id or alumno_id:
        # Aplicar los filtros solo si se proporciona al menos uno de los parámetros
        detalleDePago = ReporteEcoConceptoPago.objects.all()

        if sede_id:
            detalleDePago = detalleDePago.filter(reporteEconomico__alumno__sede_id=sede_id)

        if alumno_id:
            detalleDePago = detalleDePago.filter(reporteEconomico__alumno_id=alumno_id).distinct()
    
    # Create the HttpResponse headers with PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=PosgradoFIM-pagos-report.pdf'

    # Create the PDF object, using the BytesIO object as its "file."
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Draw the image in the header
    logo_width, logo_height = logo.size
    aspect_ratio = logo_height / logo_width
    logo_width = 250
    logo_height = logo_width * aspect_ratio
    logo_url = request.build_absolute_uri(static('pfimapp/img/logo.png'))
    c.drawImage(logo_url, 170, 730, width=logo_width, height=logo_height)

    c.setFont('Helvetica', 12)
    c.drawString(30, 905, 'Datos del Reporte de Pagos')

    c.setFont('Helvetica', 12)
    user_name = detalleDePago.first().reporteEconomico.alumno.nombre_completo().upper()  # Obtener el nombre completo del primer detalle
    user_name = user_name.split('-')[0] 
    c.drawString(30, 705, f'ALUMNO: {user_name}')

    c.setFont('Helvetica', 10)  # Cambiar la fuente a 'Helvetica' y el tamaño de fuente a 10
    # Obtener otros datos del alumno según sea necesario y mostrarlos en el encabezado
    
    # Use today() method to get current date
    current_date = datetime.today().strftime('%d/%m/%Y')
    c.drawString(480, 705, current_date)
    c.line(460, 702, 560, 702)

    # Table header
    styles = getSampleStyleSheet()
    styleBH = styles["Normal"]
    styleBH.alignment = TA_CENTER
    styleBH.fontSize = 10

    # Table data
    header = ['CONCEPTO DE PAGO', 'PERIODO', 'MONTO', 'NÚMERO DE RECIBO', 'ESTADO DE BOLETA DE PAGO']

    data = [header,]
    
    for detalle in detalleDePago:
        periodo_codigo = detalle.periodo.codigo
        # Obtener la parte del código del período que deseas mostrar
        periodo_parte_mostrar = '-'.join(periodo_codigo.split(' ')[0].split('-')[:3])

        concepto_pago = detalle.conceptoPago.nombre
        periodo = periodo_parte_mostrar
        monto = detalle.monto
        numero_recibo = detalle.numeroRecibo
        estado_boleta_pago = detalle.estadoBoletaPago.nombre

        row = [
            concepto_pago,
            periodo,
            str(monto),
            numero_recibo,
            estado_boleta_pago
        ]
        data.append(row)

    # Table style
    table = Table(data, colWidths=[4 * cm, 3 * cm, 3 * cm, 4 * cm, 5 * cm])
    table.setStyle(TableStyle([
        # Estilo de las celdas de la tabla
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Estilo de fuente
        ('FONTSIZE', (0, 0), (-1, -1), 7),  # Tamaño de fuente
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Color de fondo de la fila del encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Color de texto de la fila del encabezado
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Alineación del texto en la fila del encabezado
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Estilo de fuente
        ('FONTSIZE', (0, 1), (-1, -1), 7),  # Tamaño de fuente
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alineación del texto en todas las celdas
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alineación vertical del texto en todas las celdas
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),  # Estilo de las líneas de la tabla
    ]))

    # Table size    
    width, height = A4
    table.wrapOn(c, width, height)
    table.drawOn(c, 30, 320)  # Ajusta el valor '600' según sea necesario
    c.showPage()  # save page

    # save pdf
    c.save()
    # get the value of BytesIO buffer and write response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

@login_required
def generar_pdf_boleta_matricula(request):
    periodo_id = request.GET.get('periodo_id')
    alumno_id = request.GET.get('alumno_id')

    image_path = os.path.join(settings.STATICFILES_DIRS[0], 'pfimapp/img/logo.png')
    logo = Image.open(image_path)

    detalleAcademico = DetalleMatricula.objects.none()  # Crear un queryset vacío
    
    if periodo_id or alumno_id:
        # Aplicar los filtros solo si se proporciona al menos uno de los parámetros
        detalleAcademico = DetalleMatricula.objects.all()
        
        if periodo_id:
            detalleAcademico = detalleAcademico.filter(matricula__seccion__periodo_id=periodo_id)
                        
        if alumno_id:
            detalleAcademico = detalleAcademico.filter(matricula__alumno_id=alumno_id).distinct()

    # Create the HttpResponse headers with PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=PosgradoFIM-pagos-report.pdf'
    # Create the PDF object, using the BytesIO object as its "file."
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Draw the image in the header
    logo_width, logo_height = logo.size
    aspect_ratio = logo_height / logo_width
    logo_width = 250
    logo_height = logo_width * aspect_ratio
    logo_url = request.build_absolute_uri(static('pfimapp/img/logo.png'))
    c.drawImage(logo_url, 170, 730, width=logo_width, height=logo_height)

    c.setFont('Helvetica', 12)
    c.drawString(30, 905, 'Datos del Reporte de Pagos')

    c.setFont('Helvetica', 12)
    user_name = detalleAcademico.first().matricula.alumno.nombre_completo().upper()
    user_name = user_name.split('-')[0] 
    c.drawString(30, 705, f'ALUMNO: {user_name}')

    c.setFont('Helvetica', 10)  # Cambiar la fuente a 'Helvetica' y el tamaño de fuente a 10
    especialidad = detalleAcademico.first().seccion.maestria.nombre  # Obtener el nombre de la maestría del primer detalle
    c.drawString(30, 685, f'ESPECIALIDAD: {especialidad}')

    # Use today() method to get current date
    current_date = datetime.today().strftime('%d/%m/%Y')
    c.drawString(480, 705, current_date)
    c.line(460, 702, 560, 702)
     # Table header
    styles = getSampleStyleSheet()
    styleBH = styles["Normal"]
    styleBH.alignment = TA_CENTER
    styleBH.fontSize = 10

    # Encabezado de la tabla
    header = ['PERIODO', 'CÓDIGO', 'CRÉDITO', 'CURSO', 'DOCENTE', 'ESTADO']
    data = [header]

    # Datos de los detalles de matrícula
    for detalle in detalleAcademico:
        periodo_codigo = detalle.seccion.periodo.codigo
        # Obtener la parte del código del período que deseas mostrar
        periodo_parte_mostrar = '-'.join(periodo_codigo.split(' ')[0].split('-')[:3])
        
        periodo = periodo_parte_mostrar
        codigo = detalle.seccion.curso.codigo
        credito = detalle.seccion.curso.credito
        curso = detalle.seccion.curso.nombre
        docente = detalle.seccion.docente.usuario.nombre_completos()
        
        if detalle.retirado == 0:
            estado = 'ESTUDIANTE'
        else:
            estado = 'RETIRADO'

        row = [
            str(periodo),
            codigo,
            str(credito),
            curso,
            docente,
            estado
        ]
        data.append(row)
   
    # Estilo de la tabla
    table = Table(data, colWidths=[1.5 * cm, 1 * cm, 1 * cm, 9 * cm, 4 * cm, 2 * cm])

    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 5),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    # Ajustar tamaño y posición de la tabla
    width, height = A4    
    table.wrapOn(c, width, height)
    table.drawOn(c, 30, 550)  # Ajusta el valor '600' según sea necesario
    c.showPage()  # save page

    # save pdf
    c.save()
    # get the value of BytesIO buffer and write response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

