from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.contrib.auth.hashers import make_password
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))

Es1 = 'A'
Es2 = 'I'
ESTADO_OFERTA = [
    (Es1, 'Activo'),
    (Es2, 'Inactivo')
]

class EstadoCivil(models.Model):

    nombre = models.CharField(max_length=50)
    estado = models.CharField(max_length=1, choices=ESTADO_OFERTA, default='A')
    fechaRegistro = models.DateField(default=timezone.now)
    fechaModificado = models.DateField(null=True, blank=True, auto_now=True)
    ipUsuario = models.CharField(null=True, default=s.getsockname()[0], blank=True, max_length=100)
    usuarioPosgradoFIM = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self):
        return "{}".format(self.nombre)

    class Meta:
        verbose_name_plural = "Estado Civil"

class Sede(models.Model):

    nombre = models.CharField(max_length=50)
    estado = models.CharField(max_length=1, choices=ESTADO_OFERTA, default='A')
    fechaRegistro = models.DateField(default=timezone.now)
    fechaModificado = models.DateField(null=True, blank=True, auto_now=True)  
    ipUsuario = models.CharField(null=True, default=s.getsockname()[0], blank=True, max_length=100)
    usuarioPosgradoFIM = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self):
        return "{}".format(self.nombre)

    class Meta:
        verbose_name_plural = "Sede"

class Maestria(models.Model):

    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=100)
    estado = models.CharField(max_length=1, choices=ESTADO_OFERTA, default='A')
    fechaRegistro = models.DateField(default=timezone.now)
    fechaModificado = models.DateField(null=True, blank=True, auto_now=True)   
    ipUsuario = models.CharField(null=True, default=s.getsockname()[0], blank=True, max_length=100)
    usuarioPosgradoFIM = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self):
        return "{} - {}".format(self.codigo, self.nombre)

    class Meta:
        verbose_name_plural = "Maestrias"

class TipoDocumento(models.Model):

    nombre = models.CharField(max_length=50)
    estado = models.CharField(max_length=1, choices=ESTADO_OFERTA, default='A')
    fechaRegistro = models.DateField(default=timezone.now)
    fechaModificado = models.DateField(null=True, blank=True, auto_now=True)    
    ipUsuario = models.CharField(null=True, default=s.getsockname()[0], blank=True, max_length=100)
    usuarioPosgradoFIM = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self):
        return "{}".format(self.nombre)

    class Meta:
        verbose_name_plural = "Tipo de Documentos"

class UsuarioManager(BaseUserManager):

    def create_user(self, email, primerNombre, apellidoPaterno, segundoNombre, apellidoMaterno, password=None):
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico')
        if not primerNombre:
            raise ValueError('El usuario debe tener un primer nombre')
        if not segundoNombre:
            raise ValueError('El usuario debe tener un segundo nombre')        
        if not apellidoPaterno:
            raise ValueError('El usuario debe tener un apellido paterno')
        if not apellidoMaterno:
            raise ValueError('El usuario debe tener un apellido materno')

        user = self.model(
            email=self.normalize_email(email),
            primerNombre=primerNombre,
            segundoNombre=segundoNombre,
            apellidoPaterno=apellidoPaterno,
            apellidoMaterno=apellidoMaterno
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, primerNombre, segundoNombre,apellidoPaterno,apellidoMaterno, password):
        user = self.create_user(
            email=self.normalize_email(email),
            primerNombre=primerNombre,
            segundoNombre=segundoNombre,
            apellidoPaterno=apellidoPaterno,
            apellidoMaterno=apellidoMaterno,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(max_length=100,unique=True, error_messages={'unique': 'Este correo electrónico ya está en uso.'})
    nacionalidad = models.CharField(max_length=100)
    tipoDocumento = models.ForeignKey(TipoDocumento, null=True, on_delete=models.SET_NULL)
    numeroDocumento = models.CharField(max_length=100,unique=True, error_messages={'unique': 'Este DNI ya está en uso.'})
    numeroUbigeoNacimiento = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    # codigoEgresadoUNI = models.CharField(max_length=20,null=True, blank=True)    
    primerNombre = models.CharField(max_length=100)
    segundoNombre = models.CharField(max_length=100, null=True, blank=True)
    apellidoPaterno = models.CharField(max_length=100)
    apellidoMaterno = models.CharField(max_length=100)    
    estadoCivil = models.ForeignKey(EstadoCivil, null=True, on_delete=models.SET_NULL)
    correoUNI = models.CharField(null=True, blank=True,max_length=100)
    # gradoEstudio = models.CharField(max_length=200)
    # universidadProcedencia = models.CharField(max_length=200)
    telefono = models.CharField(max_length=15)
    fechaNacimiento = models.DateField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    fechaRegistro = models.DateField(default=timezone.now)
    fechaModificado = models.DateField(null=True, blank=True, auto_now=True)    
  
    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['primerNombre', 'segundoNombre','apellidoPaterno','apellidoMaterno']

   
        
    def nombre_completos(self):
        if self.segundoNombre:
            return "{} {} {} {}".format(self.apellidoPaterno, self.apellidoMaterno, self.primerNombre, self.segundoNombre)
        else:
            return "{} {} {}".format(self.apellidoPaterno, self.apellidoMaterno, self.primerNombre)


    def __str__(self):
        return self.nombre_completos()
  
    class Meta:
        verbose_name_plural = "Usuarios"

class EstadoBoletaP(models.Model):

    nombre = models.CharField(max_length=50)
    estado = models.CharField(max_length=1, choices=ESTADO_OFERTA, default='A')
    fechaRegistro = models.DateField(default=timezone.now)
    fechaModificado = models.DateField(null=True, blank=True, auto_now=True)    
    ipUsuario = models.CharField(null=True, default=s.getsockname()[0], blank=True, max_length=100)
    usuarioPosgradoFIM = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Estados Boletas Pagos"


class ConceptoPago(models.Model):

    nombre = models.CharField(max_length=50)
    estado = models.CharField(max_length=1, choices=ESTADO_OFERTA, default='A')
    fechaRegistro = models.DateField(default=timezone.now)
    fechaModificado = models.DateField(null=True, blank=True, auto_now=True)    
    ipUsuario = models.CharField(null=True, default=s.getsockname()[0], blank=True, max_length=100)
    usuarioPosgradoFIM = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Conceptos de Pagos"

class EstadoAcademico(models.Model):

    nombre = models.CharField(max_length=50)
    estado = models.CharField(max_length=1, choices=ESTADO_OFERTA, default='A')
    fechaRegistro = models.DateField(default=timezone.now)
    fechaModificado = models.DateField(null=True, blank=True, auto_now=True)    
    ipUsuario = models.CharField(null=True, default=s.getsockname()[0], blank=True, max_length=100)
    usuarioPosgradoFIM = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self):
        return "{}".format(self.nombre)

    class Meta:
        verbose_name_plural = "Estados Academico"

class Periodo(models.Model):

    codigo = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    estado = models.CharField(max_length=1, choices=ESTADO_OFERTA, default='A')
    fechaRegistro = models.DateField(default=timezone.now)
    fechaModificado = models.DateField(null=True, blank=True, auto_now=True)    
    ipUsuario = models.CharField(null=True, default=s.getsockname()[0], blank=True, max_length=100)
    usuarioPosgradoFIM = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self):
        return self.codigo

    class Meta:
        verbose_name_plural = "Periodos"

class Alumno(models.Model):

    usuario = models.ForeignKey(CustomUser, null=True, on_delete=models.SET_NULL)
    maestria = models.ForeignKey(Maestria, null=True, on_delete=models.SET_NULL)
    periodoDeIngreso = models.ForeignKey(Periodo, null=True, blank=True, on_delete=models.SET_NULL)
    codigoUniPreGrado = models.CharField(max_length=10, null=True, blank=True)
    codigoAlumPFIM = models.CharField(max_length=15, null=True, blank=True)
    estadoAcademico = models.ForeignKey(EstadoAcademico, null=True, on_delete=models.SET_NULL)
    estado = models.CharField(max_length=1, choices=ESTADO_OFERTA, default='A')
    fechaRegistro = models.DateField(default=timezone.now)
    fechaModificado = models.DateField(null=True, blank=True, auto_now=True)    
    ipUsuario = models.CharField(null=True, default=s.getsockname()[0], blank=True, max_length=100)
    usuarioPosgradoFIM = models.CharField(null=True, blank=True, max_length=200)
<<<<<<< HEAD

    def nombre_completo(self):            
        if self.usuario.segundoNombre:
            return "{} {} {} {}, {}".format(self.usuario.apellidoPaterno, self.usuario.apellidoMaterno, self.usuario.primerNombre, self.usuario.segundoNombre, self.maestria.codigo)
        else:
            return "{} {} {}".format(self.usuario.apellidoPaterno, self.usuario.apellidoMaterno, self.usuario.primerNombre, self.maestria.codigo)

=======
    
    def nombre_completo(self):
        if self.usuario.segundoNombre:
            return "{} {} {} {}".format(self.usuario.apellidoPaterno, self.usuario.apellidoMaterno, self.usuario.primerNombre, self.usuario.segundoNombre)
        else:
            return "{} {} {}".format(self.usuario.apellidoPaterno, self.usuario.apellidoMaterno, self.usuario.primerNombre)
        
>>>>>>> 50410a50273e667554ed63abfad5f04776b3cf62
    def __str__(self):
        return self.nombre_completo()

    class Meta:
        verbose_name_plural = "Alumnos"

class ReporteEconomico(models.Model):

    alumno = models.ForeignKey(Alumno, null=True, on_delete=models.SET_NULL)
    conceptoPago = models.ManyToManyField(ConceptoPago, through='ReporteEcoConceptoPago', blank=True,)
    estado = models.CharField(max_length=1, choices=ESTADO_OFERTA, default='A')
    fechaRegistro = models.DateField(default=timezone.now)
    fechaModificado = models.DateField(null=True, blank=True, auto_now=True)    
    ipUsuario = models.CharField(null=True, default=s.getsockname()[0], blank=True, max_length=100)
    usuarioPosgradoFIM = models.CharField(null=True, blank=True, max_length=200)

    class Meta:

        verbose_name_plural = "Reportes Economicos"


class ReporteEcoConceptoPago(models.Model):

    reporteEconomico = models.ForeignKey(ReporteEconomico, null=True, on_delete=models.SET_NULL)
    conceptoPago = models.ForeignKey(ConceptoPago, null=True, on_delete=models.SET_NULL)
    periodo = models.ForeignKey(Periodo, null=True, on_delete=models.SET_NULL)
    monto = models.FloatField()
    numeroRecibo = models.CharField(max_length=100, null=True, blank=True)
    estadoBoletaPago = models.ForeignKey(EstadoBoletaP, null=True, on_delete=models.SET_NULL)
    estado = models.CharField(max_length=1, choices=ESTADO_OFERTA, default='A')
    fechaRegistro = models.DateField(default=timezone.now)
    fechaModificado = models.DateField(null=True, blank=True, auto_now=True)    
    ipUsuario = models.CharField(null=True, default=s.getsockname()[0], blank=True, max_length=100)
    usuarioPosgradoFIM = models.CharField(null=True, blank=True, max_length=200)

class Curso(models.Model):

    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=100)
    credito = models.IntegerField()
    estado = models.CharField(max_length=1, choices=ESTADO_OFERTA, default='A')
    fechaRegistro = models.DateField(default=timezone.now)
    fechaModificado = models.DateField(null=True, blank=True, auto_now=True)    
    ipUsuario = models.CharField(null=True, default=s.getsockname()[0], blank=True, max_length=100)
    usuarioPosgradoFIM = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self):
        return "{} - {}".format(self.codigo, self.nombre)

    class Meta:
        verbose_name_plural = "Cursos"

class Docente(models.Model):

    usuario = models.ForeignKey(CustomUser, null=True, on_delete=models.SET_NULL)
    maestria = models.ForeignKey(Maestria, null=True, on_delete=models.SET_NULL)
    estado = models.CharField(max_length=1, choices=ESTADO_OFERTA, default='A')
    fechaRegistro = models.DateField(default=timezone.now)
    fechaModificado = models.DateField(null=True, blank=True, auto_now=True)    
    ipUsuario = models.CharField(null=True, default=s.getsockname()[0], blank=True, max_length=100)
    usuarioPosgradoFIM = models.CharField(null=True, blank=True, max_length=200)

    def nombre_completo(self):        
        if self.usuario.segundoNombre:
            return "{} {} {} {}, {}".format(self.usuario.apellidoPaterno, self.usuario.apellidoMaterno, self.usuario.primerNombre, self.usuario.segundoNombre, self.maestria.codigo)
        else:
            return "{} {} {}, {}".format(self.usuario.apellidoPaterno, self.usuario.apellidoMaterno, self.usuario.primerNombre, self.maestria.codigo)


    def __str__(self):
        return self.nombre_completo()

    class Meta:
        verbose_name_plural = "Docentes"

class DefinicionCalificacion(models.Model):
    nombre = models.CharField(max_length=50)
    porcentaje = models.IntegerField()
    seccion = models.ForeignKey('Seccion', on_delete=models.CASCADE)  # revisar si funciona

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Tipos de Calificaciones"

class Seccion(models.Model):

    maestria = models.ForeignKey(Maestria, null=True, on_delete=models.SET_NULL)
    periodo = models.ForeignKey(Periodo, null=True, on_delete=models.SET_NULL)
    curso = models.ForeignKey(Curso, null=True, on_delete=models.SET_NULL)
    docente = models.ForeignKey(Docente, null=True, on_delete=models.SET_NULL)     
    aulaWeb = models.CharField(max_length=100, null=True, blank=True)
    estado = models.CharField(max_length=1, choices=ESTADO_OFERTA, default='A')
    fechaRegistro = models.DateField(default=timezone.now)
    fechaModificado = models.DateField(null=True, blank=True, auto_now=True)    
    ipUsuario = models.CharField(null=True, default=s.getsockname()[0], blank=True, max_length=100)
    usuarioPosgradoFIM = models.CharField(null=True, blank=True, max_length=200)

    def nombre_completo(self):
        return "{} / {} {} {} / {} {} {}".format(self.periodo.codigo, self.maestria.codigo, self.curso.codigo, self.curso.nombre, self.docente.usuario.apellidoPaterno, self.docente.usuario.apellidoMaterno, self.docente.usuario.primerNombre)

    def __str__(self):
        return self.nombre_completo()

    class Meta:
        verbose_name_plural = "Secciones"

# class DetalleSeccion(models.Model):
#     seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE)
#     tipoCalificacion = models.ForeignKey(TipoCalificacion, null=True, on_delete=models.SET_NULL)    
#     estado = models.CharField(max_length=1, choices=ESTADO_OFERTA, default='A')
#     fechaRegistro = models.DateField(default=timezone.now)
#     fechaModificado = models.DateField(null=True, blank=True, auto_now=True)    
#     ipUsuario = models.CharField(null=True, default=s.getsockname()[0], blank=True, max_length=100)
#     usuarioPosgradoFIM = models.CharField(null=True, blank=True, max_length=200)

#     def __str__(self):
        
#         maestria = self.seccion.maestria
#         curso = self.seccion.curso
#         docente = self.seccion.docente.usuario
#         periodo = self.seccion.periodo

#         return f"{periodo.codigo}/ {maestria.codigo}/ {curso.codigo}/ Docente: {docente}/ {self.tipoCalificacion}"

#     class Meta:
#         verbose_name_plural = "Detalle Seccion"

class Matricula(models.Model):
    alumno = models.ForeignKey(Alumno, null=True, on_delete=models.SET_NULL)
    seccion = models.ManyToManyField(Seccion, through='DetalleMatricula', blank=True,)    
    estado = models.CharField(max_length=1, choices=ESTADO_OFERTA, default='A')
    fechaRegistro = models.DateField(default=timezone.now)
    fechaModificado = models.DateField(null=True, blank=True, auto_now=True)    
    ipUsuario = models.CharField(null=True, default=s.getsockname()[0], blank=True, max_length=100)
    usuarioPosgradoFIM = models.CharField(null=True, blank=True, max_length=200)

    def get_periodo(self):
        return self.seccion.first().periodo.codigo if self.seccion.exists() else None
    
    def nombre_completo(self):
        
            if self.alumno.usuario.segundoNombre:
                
                return "{} {}, {} {}".format(
                    self.alumno.usuario.apellidoPaterno,
                    self.alumno.usuario.apellidoMaterno,
                    self.alumno.usuario.primerNombre,
                    self.alumno.usuario.segundoNombre,                    
                )
            else:
                
                return "{} {} {}".format(
                    self.alumno.usuario.apellidoPaterno,
                    self.alumno.usuario.apellidoMaterno,
                    self.alumno.usuario.primerNombre,                    
                )
        

    def __str__(self):        
        return self.nombre_completo()

    class Meta:
        verbose_name_plural = "Matriculas"

class DetalleMatricula(models.Model):
    matricula = models.ForeignKey(Matricula, null=True, on_delete=models.SET_NULL) # revisar
    seccion = models.ForeignKey(Seccion, null=True, on_delete=models.SET_NULL) # revisar
    nota_final = models.FloatField(null=True, blank=True)     
    retirado = models.BooleanField(default=False)
    estado = models.CharField(max_length=1, choices=ESTADO_OFERTA, default='A')
    fechaRegistro = models.DateField(default=timezone.now)
    fechaModificado = models.DateField(null=True, blank=True, auto_now=True)    
    ipUsuario = models.CharField(null=True, default=s.getsockname()[0], blank=True, max_length=100)
    usuarioPosgradoFIM = models.CharField(null=True, blank=True, max_length=200)

    
    def __str__(self):
        
        curso = self.seccion.curso
        periodo = self.seccion.periodo
        alumno = self.matricula.alumno.usuario
        return f"{alumno.apellidoPaterno} {alumno.apellidoMaterno}, {curso}, {periodo}"
    
    def calcular_nota_final(self):
        #calificaciones # referencia inversa
        # for calificacion
        # sumatoria ( calificacion.definicionCalificacion.porcentaje * calificacion.nota) /100
        #self.nota_final = resultasdo
        pass

    class Meta:
        verbose_name_plural = "Detalle de Matriculas"

class Calificacion(models.Model):
    detalle_matricula = models.ForeignKey(DetalleMatricula, on_delete=models.CASCADE)
    definicionCalificacion = models.ForeignKey(DefinicionCalificacion, on_delete=models.CASCADE)
    nota = models.FloatField(null=True)     
    fecha_calificacion = models.DateField(default=timezone.now)
   
    def __str__(self):
        alumno = self.matricula.alumno
        maestria = self.matricula.seccion.maestria
        curso = self.matricula.seccion.curso
        docente = self.matricula.seccion.docente
        s
        return f"Calificación de {alumno} en {maestria} / {curso} / {docente} / Nota: {self.nota})"

    class Meta:
        verbose_name_plural = "Calificaciones"


