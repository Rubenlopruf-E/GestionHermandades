from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from datetime import date
from django.contrib.auth.models import User


class EstadoHermano(models.TextChoices):
    ACTIVO = 'Activo', 'Activo'
    INACTIVO = 'Inactivo', 'Inactivo'
    SUSPENDIDO = 'Suspendido', 'Suspendido'

class Hermano(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField()
    fecha_ingreso = models.DateField()
    estado = models.CharField(
        max_length=10,
        choices=EstadoHermano.choices,
        default=EstadoHermano.ACTIVO
    )
    imagen = models.ImageField(upload_to='hermanos/', blank=True, null=True)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)

    def clean(self):
        edad = date.today().year - self.fecha_nacimiento.year # Calcular la edad
        if edad < 0 or edad > 120:
            raise ValidationError("Edad no válida.")

    def __str__(self):
        return f"{self.nombre} {self.apellidos} ({self.dni})"

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    hermanos = models.ManyToManyField(Hermano, through='HermanoRol', related_name='roles') 
    #Esto lo añado yo en admin

    def __str__(self):
        return self.nombre

class HermanoRol(models.Model):
    hermano = models.ForeignKey(Hermano, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = ('hermano', 'rol')

    def __str__(self):
        return f"{self.hermano} - {self.rol}"

class EstadoPago(models.TextChoices):
    PENDIENTE = 'Pendiente', 'Pendiente'
    PAGADO = 'Pagado', 'Pagado'

class PeriodoCuota(models.TextChoices):
    SEMESTRE_1 = 'sem1', '1er Semestre'
    SEMESTRE_2 = 'sem2', '2do Semestre'
    # TRIMESTRE_1 = 'trim1', '1er Trimestre'
    # TRIMESTRE_2 = 'trim2', '2do Trimestre'
    # TRIMESTRE_3 = 'trim3', '3er Trimestre'
    # TRIMESTRE_4 = 'trim4', '4to Trimestre'
    # CUATRIMESTRE_1 = 'cuat1', '1er Cuatrimestre'
    # CUATRIMESTRE_2 = 'cuat2', '2do Cuatrimestre'
    # CUATRIMESTRE_3 = 'cuat3', '3er Cuatrimestre'
    # ANUAL = 'anual', 'Anual'

class Cuota(models.Model):
    hermano = models.ForeignKey(Hermano, on_delete=models.CASCADE, related_name='cuotas')
    importe = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    fecha = models.DateField(auto_now_add=True)
    estado_pago = models.CharField(max_length=10, choices=EstadoPago.choices, default=EstadoPago.PENDIENTE)
    periodo = models.CharField(max_length=10, choices=PeriodoCuota.choices, default=PeriodoCuota.SEMESTRE_1)

    def clean(self):
        if self.importe <= 0:
            raise ValidationError("El importe debe ser mayor que cero.")

    def __str__(self):
        return f"Cuota {self.importe} - {self.hermano} - {self.get_periodo_display()} - {self.estado_pago}"

class TipoCulto(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre
    #Esto lo añado yo en admin


class Culto(models.Model):
    tipo = models.ForeignKey(TipoCulto, on_delete=models.CASCADE)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    hermanos = models.ManyToManyField(Hermano, through='ParticipacionCulto', related_name='cultos')

    def __str__(self):
        return f"{self.tipo.nombre} el {self.fecha_inicio}" 

class ParticipacionCulto(models.Model):
    hermano = models.ForeignKey(Hermano, on_delete=models.CASCADE)
    culto = models.ForeignKey(Culto, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    tramo = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('hermano', 'culto', 'rol')

    def __str__(self):
        return f"{self.hermano} como {self.rol} en {self.culto}"
