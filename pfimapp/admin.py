from django.contrib import admin
from pfimapp.models import DefinicionCalificacion,DetalleMatricula,Matricula,Seccion,Docente,Curso,CustomUser,TipoDocumento,Maestria,EstadoCivil,Sede,ReporteEcoConceptoPago,ReporteEconomico,ConceptoPago,Periodo,Alumno,EstadoAcademico,EstadoBoletaP
from django import forms
from django.contrib.auth.hashers import make_password
# Register your models here.

class DefinicionCalificacionAdmin(admin.TabularInline):
    model = DefinicionCalificacion
    extra = 1

class SeccionAdmin(admin.ModelAdmin):    
    # Para que sea mas facil de encontrar a la hora de crear una matricula
    search_fields = ['periodo__codigo', 'maestria__codigo', 'curso__codigo']
    autocomplete_fields = ['curso', 'periodo', 'docente', 'maestria']
    # --- poner en solo lectura los input ---
    exclude = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
    readonly_fields = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
# ----- Fin poner en solo lectura los input -----
    list_display = ('curso', 'docente', 'periodo', 'maestria',
                    'aulaWeb', 'estado', 'fechaRegistro')
    inlines = [DefinicionCalificacionAdmin,]

    def save_model(self, request, obj, form, change):
        # request.user es el usuario autenticado en ese momento

        obj.usuarioPosgradoFIM = request.user.apellidoPaterno+' '+request.user.apellidoMaterno+' '+request.user.primerNombre
        super().save_model(request, obj, form, change)

admin.site.register(Seccion, SeccionAdmin)

class DocenteAdmin(admin.ModelAdmin):
    search_fields = ['usuario__apellidoPaterno', 'usuario__numeroDocumento']
    autocomplete_fields = ['usuario','maestria']
    # --- poner en solo lectura los input ---
    exclude = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
    readonly_fields = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
# ----- Fin poner en solo lectura los input -----
    list_display = ('usuario', 'maestria', 'estado', 'fechaRegistro')

    def save_model(self, request, obj, form, change):
        # request.user es el usuario autenticado en ese momento

        obj.usuarioPosgradoFIM = request.user.apellidoPaterno+' '+request.user.apellidoMaterno+' '+request.user.primerNombre
        super().save_model(request, obj, form, change)


admin.site.register(Docente, DocenteAdmin)

class CursoAdmin(admin.ModelAdmin):
    search_fields = ['codigo','nombre']
    ordering = ['codigo']
    # --- poner en solo lectura los input ---
    exclude = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
    readonly_fields = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
# ----- Fin poner en solo lectura los input -----
    list_display = ('codigo', 'nombre', 'credito', 'estado', 'fechaRegistro')

    def save_model(self, request, obj, form, change):
        # request.user es el usuario autenticado en ese momento

        obj.usuarioPosgradoFIM = request.user.apellidoPaterno+' '+request.user.apellidoMaterno+' '+request.user.primerNombre
        super().save_model(request, obj, form, change)


admin.site.register(Curso, CursoAdmin)

class UserAdmin(admin.ModelAdmin):
    search_fields = ['apellidoPaterno', 'email', 'numeroDocumento']
    ordering = ['-id']
    list_display = ('tipoDocumento', 'numeroDocumento', 'numeroUbigeoNacimiento','primerNombre', 'segundoNombre',
                    'apellidoPaterno', 'apellidoMaterno', 'email','correoUNI','telefono')
    
    def save_model(self, request, obj, form, change):
        # Si se está creando un nuevo usuario o se está cambiando el password, encripta el password antes de guardarlo
        if not obj.pk or 'password' in form.changed_data:
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)

admin.site.register(CustomUser, UserAdmin)

class PeriodoAdmin(admin.ModelAdmin):
    search_fields = ['codigo']
    ordering = ['codigo']
    # --- poner en solo lectura los input ---
    exclude = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
    readonly_fields = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
# ----- Fin poner en solo lectura los input -----
    list_display = ('codigo', 'nombre', 'estado', 'fechaRegistro')

    def save_model(self, request, obj, form, change):
        # request.user es el usuario autenticado en ese momento

        obj.usuarioPosgradoFIM = request.user.apellidoPaterno+' '+request.user.apellidoMaterno+' '+request.user.primerNombre
        super().save_model(request, obj, form, change)


admin.site.register(Periodo, PeriodoAdmin)

class TipoDocumentoAdmin(admin.ModelAdmin):
    search_fields = ['nombre']
    ordering = ['nombre']
    # --- poner en solo lectura los input ---
    exclude = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
    readonly_fields = ('fechaRegistro','usuarioPosgradoFIM', 'ipUsuario')
# ----- Fin poner en solo lectura los input -----
    list_display = ('nombre', 'estado', 'fechaRegistro')

    def save_model(self, request, obj, form, change):
        # request.user es el usuario autenticado en ese momento

        obj.usuarioPosgradoFIM = request.user.apellidoPaterno+' '+request.user.apellidoMaterno+' '+request.user.primerNombre
        super().save_model(request, obj, form, change)

admin.site.register(TipoDocumento, TipoDocumentoAdmin)

class EstadoBoletaPAdmin(admin.ModelAdmin):
    search_fields = ['nombre']
    ordering = ['nombre']
    # --- poner en solo lectura los input ---
    exclude = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
    readonly_fields = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
# ----- Fin poner en solo lectura los input -----
    list_display = ('nombre', 'estado', 'fechaRegistro')

    def save_model(self, request, obj, form, change):
        # request.user es el usuario autenticado en ese momento

        obj.usuarioPosgradoFIM = request.user.apellidoPaterno+' '+request.user.apellidoMaterno+' '+request.user.primerNombre
        super().save_model(request, obj, form, change)


admin.site.register(EstadoBoletaP, EstadoBoletaPAdmin)

class SedeAdmin(admin.ModelAdmin):
    search_fields = ['nombre']
    ordering = ['nombre']
    # --- poner en solo lectura los input ---
    exclude = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
    readonly_fields = ('fechaRegistro', 'usuarioPosgradoFIM', 'ipUsuario')
# ----- Fin poner en solo lectura los input -----
    list_display = ('nombre', 'estado', 'fechaRegistro')

    def save_model(self, request, obj, form, change):
        # request.user es el usuario autenticado en ese momento

        obj.usuarioPosgradoFIM = request.user.apellidoPaterno+' '+request.user.apellidoMaterno+' '+request.user.primerNombre
        super().save_model(request, obj, form, change)

admin.site.register(Sede, SedeAdmin)

class EstadoCivilAdmin(admin.ModelAdmin):
    search_fields = ['nombre']
    ordering = ['nombre','fechaRegistro']
    # --- poner en solo lectura los input ---
    exclude = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
    readonly_fields = ('fechaRegistro', 'usuarioPosgradoFIM', 'ipUsuario')
# ----- Fin poner en solo lectura los input -----
    list_display = ('nombre', 'estado', 'fechaRegistro')

    def save_model(self, request, obj, form, change):
        # request.user es el usuario autenticado en ese momento

        obj.usuarioPosgradoFIM = request.user.apellidoPaterno+' '+request.user.apellidoMaterno+' '+request.user.primerNombre
        super().save_model(request, obj, form, change)

admin.site.register(EstadoCivil, EstadoCivilAdmin)

class EstadoAcademicoAdmin(admin.ModelAdmin):
    search_fields = ['nombre']
    ordering = ['nombre']
    
    # --- poner en solo lectura los input ---
    exclude = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
    readonly_fields = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
# ----- Fin poner en solo lectura los input -----
    list_display = ('nombre', 'estado', 'fechaRegistro', 'usuarioPosgradoFIM')

    def save_model(self, request, obj, form, change):
        # request.user es el usuario autenticado en ese momento

        obj.usuarioPosgradoFIM = request.user.apellidoPaterno+' '+request.user.apellidoMaterno+' '+request.user.primerNombre
        super().save_model(request, obj, form, change)

admin.site.register(EstadoAcademico, EstadoAcademicoAdmin)


class MaestriaAdmin(admin.ModelAdmin):
    search_fields = ['codigo']
    ordering = ['codigo']
   
    # --- poner en solo lectura los input ---
    exclude = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
    readonly_fields = ('fechaRegistro', 'usuarioPosgradoFIM', 'ipUsuario')
# ----- Fin poner en solo lectura los input -----
    list_display = ('codigo', 'nombre', 'estado', 'fechaRegistro')

    def save_model(self, request, obj, form, change):
        # request.user es el usuario autenticado en ese momento

        obj.usuarioPosgradoFIM = request.user.apellidoPaterno+' '+request.user.apellidoMaterno+' '+request.user.primerNombre
        super().save_model(request, obj, form, change)


admin.site.register(Maestria, MaestriaAdmin)

class AlumnoAdmin(admin.ModelAdmin):
    search_fields = ['usuario__apellidoPaterno', 'usuario__numeroDocumento']
    autocomplete_fields = ['usuario', 'periodoDeIngreso','maestria']
    # --- poner en solo lectura los input ---
    exclude = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
    readonly_fields = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
# ----- Fin poner en solo lectura los input -----
    list_display = ('usuario', 'maestria', 'periodoDeIngreso',
                    'codigoUniPreGrado', 'estadoAcademico', 'estado', 'fechaRegistro')
   
    def save_model(self, request, obj, form, change):
        # request.user es el usuario autenticado en ese momento

        obj.usuarioPosgradoFIM = request.user.apellidoPaterno+' '+request.user.apellidoMaterno+' '+request.user.primerNombre
        super().save_model(request, obj, form, change)


admin.site.register(Alumno, AlumnoAdmin)

class ConceptoPagoAdmin(admin.ModelAdmin):
    search_fields = ['nombre']
    ordering = ['nombre']
    # --- poner en solo lectura los input ---
    exclude = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
    readonly_fields = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
# ----- Fin poner en solo lectura los input -----
    list_display = ('nombre', 'estado', 'fechaRegistro')

    def save_model(self, request, obj, form, change):
        # request.user es el usuario autenticado en ese momento

        obj.usuarioPosgradoFIM = request.user.apellidoPaterno+' '+request.user.apellidoMaterno+' '+request.user.primerNombre
        super().save_model(request, obj, form, change)


admin.site.register(ConceptoPago, ConceptoPagoAdmin)

class ReporteEcoConceptoPagoAdmin(admin.TabularInline):
    model = ReporteEcoConceptoPago
    extra = 0
  
    autocomplete_fields = ['conceptoPago', 'periodo']
    # --- poner en solo lectura los input ---
    exclude = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
    readonly_fields = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
# ----- Fin poner en solo lectura los input -----
    def save_model(self, request, obj, form, change):
        # request.user es el usuario autenticado en ese momento

        obj.usuarioPosgradoFIM = f'{request.user.apellidoPaterno} {request.user.apellidoMaterno} {request.user.primerNombre}'
        super().save_model(request, obj, form, change)


class ReporteEconomicoAdmin(admin.ModelAdmin):
    search_fields = ['alumno__usuario__apellidoPaterno',
                     'alumno__usuario__numeroDocumento']
    autocomplete_fields = ['alumno']
    inlines = [ReporteEcoConceptoPagoAdmin, ]
    # --- poner en solo lectura los input ---
    exclude = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
    readonly_fields = ('fechaRegistro', 'fechaModificado','usuarioPosgradoFIM', 'ipUsuario')
# ----- Fin poner en solo lectura los input -----
    list_display = ('alumno', 'estado', 'fechaRegistro')
    filter_horizontal = ['conceptoPago']

    def save_model(self, request, obj, form, change):
        # request.user es el usuario autenticado en ese momento
        obj.usuarioPosgradoFIM = f'{request.user.apellidoPaterno} {request.user.apellidoMaterno} {request.user.primerNombre}'
        super().save_model(request, obj, form, change)


admin.site.register(ReporteEconomico, ReporteEconomicoAdmin)

class DetalleMatriculaAdmin(admin.TabularInline):
    model = DetalleMatricula
    extra = 1
    
    autocomplete_fields = ['seccion']
    readonly_fields = ('fechaRegistro', 'fechaModificado', 'usuarioPosgradoFIM', 'ipUsuario')

    def save_model(self, request, obj, form, change):
        obj.usuarioPosgradoFIM = f"{request.user.apellidoPaterno} {request.user.apellidoMaterno} {request.user.primerNombre}"
        super().save_model(request, obj, form, change)

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    search_fields = ['alumno__usuario__apellidoPaterno', 'alumno__usuario__numeroDocumento', 'seccion__periodo__codigo']
    autocomplete_fields = ['alumno',]
    inlines = [DetalleMatriculaAdmin, ]
    exclude = ('fechaRegistro', 'fechaModificado', 'usuarioPosgradoFIM', 'ipUsuario')
    readonly_fields = ('fechaRegistro', 'fechaModificado', 'usuarioPosgradoFIM', 'ipUsuario')
    list_display = ('alumno','get_periodo', 'estado', 'fechaRegistro')
    filter_horizontal = ['seccion']
   
    def save_model(self, request, obj, form, change):
        # Guardar el usuario que realizó la matrícula
        if not change:
            obj.usuarioPosgradoFIM = f"{request.user.apellidoPaterno} {request.user.apellidoMaterno} {request.user.primerNombre}"
        super().save_model(request, obj, form, change)

    def get_periodo(self, obj):
        # Esta función es para mostrar el periodo en la lista, pero no es utilizado para la búsqueda.
        return obj.seccion.first().periodo.codigo if obj.seccion.exists() else None

    get_periodo.admin_order_field = 'seccion__periodo__codigo'
    get_periodo.short_description = 'Periodo'

