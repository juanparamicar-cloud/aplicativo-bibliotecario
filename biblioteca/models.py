from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg

def validar_correo_uninpahu(correo):
    if not correo.lower().endswith("@uninpahu.edu.co"):
        raise ValidationError("Usa tu correo institucional @uninpahu.edu.co")

class Libro(models.Model):
    TIPOS = [
        ("novela", "Novela"),
        ("cuento", "Cuento"),
        ("poesia", "Poesía"),
        ("ensayo", "Ensayo"),
        ("academico", "Académico"),
        ("infantil", "Infantil"),
        ("otro", "Otro"),
    ]

    nombre = models.CharField(max_length=200)
    autor = models.CharField(max_length=150)
    editorial = models.CharField(max_length=150)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    anio_publicacion = models.PositiveIntegerField(null=True, blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    descripcion = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    def promedio(self):
        return self.resenas.filter(visible=True).aggregate(Avg("puntuacion"))["puntuacion__avg"]

    def total_resenas(self):
        return self.resenas.filter(visible=True).count()

class Resena(models.Model):
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name="resenas")
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(validators=[validar_correo_uninpahu])
    puntuacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField()
    acepta_datos = models.BooleanField(default=False)
    visible = models.BooleanField(default=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.correo = self.correo.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} – {self.libro} ({self.puntuacion})"
