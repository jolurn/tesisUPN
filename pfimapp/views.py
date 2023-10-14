from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import  AuthenticationForm
<<<<<<< HEAD
from pfimapp.models import Seccion,Curso,Periodo,Docente,ReporteEconomico,ReporteEcoConceptoPago,CustomUser,Matricula,DetalleMatricula,Alumno,Sede,Maestria,TipoDocumento,EstadoCivil
=======
from pfimapp.models import Periodo,DetalleMatricula,ReporteEconomico,ReporteEcoConceptoPago,CustomUser,Matricula,DetalleMatricula,Alumno,Sede,Maestria,TipoDocumento,EstadoCivil
>>>>>>> 50410a50273e667554ed63abfad5f04776b3cf62
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

<<<<<<< HEAD
from django.http import JsonResponse

=======
from django.contrib.admin.views.decorators import staff_member_required

from django.http import JsonResponse

import re
from django.db.models import F

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
    alumnos = Alumno.objects.filter(matricula__seccion__periodo_id=periodo_id, estado="A").distinct()
    
    alumnos_list = [{'id': alumno.id, 'nombre_completo': alumno.usuario.nombre_completos().upper()} for alumno in alumnos]
    
    return JsonResponse({'alumnos': alumnos_list})

@login_required
def obtener_alumnos_por_sede(request):
    sede_id = request.GET.get('sede_id')
    alumnos = Alumno.objects.filter(usuario__sede_id=sede_id, estado="A").order_by('usuario__apellidoPaterno')
    alumnos_list = [{'id': alumno.id, 'nombre_completo': alumno.usuario.nombre_completos()} for alumno in alumnos]
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
    periodos = Periodo.objects.filter(matricula__isnull=False).distinct()
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

        print("detalleAcademico: ", detalleAcademico)
    
    boletas_disponibles = detalleAcademico.exists()

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
            detalleDePago = detalleDePago.filter(reporteEconomico__alumno__usuario__sede_id=sede_id)            
            alumnos = alumnos.filter(id=alumno_id, usuario__sede_id=sede_id)

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
                
        # Aplicar los filtros solo si se proporciona al menos uno de los parámetros
        detalleAcademico = DetalleMatricula.objects.all()

        if sede_id:
            detalleAcademico = detalleAcademico.filter(matricula__alumno__usuario__sede_id=sede_id).order_by(F('seccion__periodo__codigo'))
            # detalleAcademico = detalleAcademico.filter(matricula__alumno__usuario__sede_id=sede_id)
            alumnos = alumnos.filter(id=alumno_id, usuario__sede_id=sede_id)

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
    
    return render(request, 'reporte_calificaciones.html', {
        'detalleAcademico': detalleAcademico,
        'sedes': sedes,
        'alumnos': alumnos,
        'resultados_disponibles': resultados_disponibles,
        'alumno_actual': alumno_actual,
        'sede_id': sede_id,
        'alumno_id': alumno_id,
    })


>>>>>>> 50410a50273e667554ed63abfad5f04776b3cf62
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
        matriculas = Matricula.objects.filter(alumno__usuario=request.user, estado="A")
    except Matricula.DoesNotExist:
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
        logout(self.request)
        return response

@login_required
def generar_pdf(request):
    image_path = os.path.join(settings.STATICFILES_DIRS[0], 'pfimapp/img/logo.png')
    logo = Image.open(image_path)

    reporteAcademicos = DetalleMatricula.objects.filter(matricula__alumno__usuario=request.user, estado="A").order_by('seccion__periodo__codigo')
           
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
    header = [    'Periodo','Código','Curso','Crédito','Docente', 'Promedio','Retirado']

    # datos de la tabla
    data = [    header,]
    high = 650
    for detalle in reporteAcademicos:
        student = [
            str(detalle.seccion.periodo.codigo),
            str(detalle.seccion.curso.codigo),
            str(detalle.seccion.curso.nombre),
            str(detalle.seccion.curso.credito),
            str(detalle.seccion.docente.usuario.nombre_completos()),            
            str(detalle.promedioFinal),
            str(detalle.retirado),
        ]
        data.append(student)
        high = high - 18
    #table size
    width, height = A4
    table = Table(data, colWidths=[1.4 * cm,0.9 * cm, 8.5 * cm,0.9 * cm, 4.5 * cm, 1.4 *cm, 1.4*cm])
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

<<<<<<< HEAD
def seleccionar_periodo_maestria_curso(request):
    # Verificar si el usuario está autenticado y es un docente
    try:
        docente = Docente.objects.get(usuario=request.user)
    except Docente.DoesNotExist:
        # Si el usuario autenticado no es un docente, mostrar un mensaje de error
        return render(request, 'error_no_docente.html')

    # Obtener todos los periodos
    secciones = Seccion.objects.filter(docente=docente)

    # Obtener los períodos relacionados con las secciones
    periodos = Periodo.objects.filter(id__in=secciones.values_list('periodo', flat=True))

    # Obtener todas las maestrías relacionadas con las secciones
    maestrias = Maestria.objects.filter(id__in=secciones.values_list('maestria', flat=True))

    # Obtener todos los cursos relacionados con las secciones
    cursos = Curso.objects.filter(id__in=secciones.values_list('curso', flat=True))


    return render(request, 'seleccionar_periodo_maestria_curso.html', {
        'periodos': periodos,
        'maestrias': maestrias,
        'cursos': cursos,
    })

def guardar_calificaciones(request):
    if request.method == 'POST':
        periodo_id = request.POST.get('periodo_id')
        maestria_id = request.POST.get('maestria_id')
        curso_id = request.POST.get('curso_id')

        # Procesar el formulario enviado por el docente con las calificaciones ingresadas
        alumnos_matriculados = Alumno.objects.filter(
            matricula__seccion__periodo_id=periodo_id,
            matricula__seccion__maestria_id=maestria_id,
            matricula__seccion__curso_id=curso_id
        ).distinct()
        
        for matricula in alumnos_matriculados:
            calificacion = float(request.POST.get(f'calificacion_{matricula.id}', 0))
            detalle_matricula, _ = DetalleMatricula.objects.get_or_create(matricula=matricula)
            detalle_matricula.nota = calificacion
            detalle_matricula.save()

        # Redireccionar a la vista 'ingresar_calificaciones' nuevamente
        return redirect('ingresar_calificaciones')

    # Si el método es GET, mostrar el formulario para ingresar calificaciones
    return render(request, 'ingresar_calificaciones.html', {
        'alumnos_matriculados': alumnos_matriculados,
    })

def ingresar_calificaciones(request, periodo_id, maestria_id, curso_id):
    # Obtener la lista de alumnos matriculados para el período, maestría y curso seleccionados
    alumnos_matriculados = Alumno.objects.filter(
        matricula__seccion__periodo_id=periodo_id,
        matricula__seccion__maestria_id=maestria_id,
        matricula__seccion__curso_id=curso_id
    ).distinct()

    if request.method == 'POST':
        # Procesar el formulario enviado por el docente con las calificaciones ingresadas
        for matricula in alumnos_matriculados:
            calificacion = float(request.POST.get(f'calificacion_{matricula.id}', 0))
            detalle_matricula, _ = DetalleMatricula.objects.get_or_create(matricula=matricula)
            detalle_matricula.nota = calificacion
            detalle_matricula.save()

        # Redireccionar a otra vista después de guardar las calificaciones
        return redirect('nombre_de_la_vista')  # Cambiar 'nombre_de_la_vista' por el nombre de la vista a la que deseas redireccionar
   
    return render(request, 'ingresar_calificaciones.html', {
        'alumnos_matriculados': alumnos_matriculados,
    })

def get_maestrias(request):
    if request.method == 'GET':
        periodo_id = request.GET.get('periodo_id')
        # Lógica para obtener las maestrías asociadas al período
        
        if periodo_id:
            maestrias = Maestria.objects.filter(seccion__periodo_id=periodo_id).distinct()            
            data = [{'id': maestria.id, 'nombre': maestria.nombre} for maestria in maestrias]
        else:
            data = []

        return JsonResponse({'maestrias': data}, safe=False)
    else:
        return JsonResponse([], safe=False)
    
def get_cursos(request):
    if request.method == 'GET':
        periodo_id = request.GET.get('periodo_id')
        maestria_id = request.GET.get('maestria_id')
        
        # Lógica para obtener los cursos asociados al período y la maestría seleccionados
        if periodo_id and maestria_id:
            cursos = Curso.objects.filter(seccion__periodo_id=periodo_id, seccion__maestria_id=maestria_id).distinct()
            data = [{'id': curso.id, 'nombre': curso.nombre} for curso in cursos]
        else:
            data = []        
        return JsonResponse({'cursos': data}, safe=False)
    else:
        return JsonResponse([], safe=False)


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
        for alumno in alumnos:
            detalle_matricula = DetalleMatricula.objects.get(matricula=alumno, seccion=seccion)
            detalle_matricula.calcular_nota_final()

    return render(request, 'editar_nota.html', {
        'seccion': seccion,
        'alumnos': alumnos,
        'definiciones': definiciones,
    })
=======
# pdf de administrador

@login_required
def generar_pdf_administrativo(request):
    sede_id = request.GET.get('sede')
    alumno_id = request.GET.get('alumno')
    
    image_path = os.path.join(settings.STATICFILES_DIRS[0], 'pfimapp/img/logo.png')
    logo = Image.open(image_path)

    detalleAcademico = DetalleMatricula.objects.none()  # Crear un queryset vacío

    if sede_id or alumno_id:
        # Aplicar los filtros solo si se proporciona al menos uno de los parámetros
        detalleAcademico = DetalleMatricula.objects.all()

        if sede_id:
            detalleAcademico = detalleAcademico.filter(matricula__alumno__usuario__sede_id=sede_id)

        if alumno_id:
            detalleAcademico = detalleAcademico.filter(matricula__alumno_id=alumno_id).distinct()
    
    # Create the HttpResponse headers with PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=PosgradoFIM-student-report.pdf'

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
    c.drawString(30, 905, 'Datos del Reporte Académico')

    c.setFont('Helvetica', 12)
    user_name = detalleAcademico.first().matricula.alumno.nombre_completo()  # Obtener el nombre completo del primer detalle
    c.drawString(30, 705, f'ALUMNO: {user_name.upper()}')

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

    # Table data
    header = ['Periodo', 'Código', 'Curso', 'Crédito', 'Docente', 'Promedio', 'Retirado']
    data = [header,]
    high = 650

    for detalle in detalleAcademico:
        periodo_codigo = detalle.seccion.periodo.codigo
        # Obtener la parte del código del período que deseas mostrar
        periodo_parte_mostrar = '-'.join(periodo_codigo.split(' ')[0].split('-')[:3])
    
        student = [
            str(periodo_parte_mostrar),
            str(detalle.seccion.curso.codigo),
            str(detalle.seccion.curso.nombre),
            str(detalle.seccion.curso.credito),
            str(detalle.seccion.docente.usuario.nombre_completos()),            
            str(detalle.promedioFinal),
            str(detalle.retirado),
        ]
        data.append(student)
        high = high - 18
    width, height = A4
    table = Table(data, colWidths=[1.4 * cm,0.9 * cm, 8.5 * cm,0.9 * cm, 4.5 * cm, 1.4 *cm, 1.4*cm])
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
            detalleDePago = detalleDePago.filter(reporteEconomico__alumno__usuario__sede_id=sede_id)

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
    table.drawOn(c, 30, 350)  # Ajusta el valor '600' según sea necesario
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
>>>>>>> 50410a50273e667554ed63abfad5f04776b3cf62
