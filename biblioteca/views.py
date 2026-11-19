from django.shortcuts import render ,get_object_or_404 , redirect
from django.db.models import Avg, Count, Q
from .forms import ResenaForm
from .models import Libro,Resena
# importaciones para funcionamient de el service de ia
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .servicios_ia import obtener_recomendaciones

def catalogo(request):
    libros = Libro.objects.order_by("nombre")

    tipo = request.GET.get("tipo", "")
    if tipo:
        libros = libros.filter(tipo=tipo)

    context = {
        "libros": libros,
        "tipos": Libro.TIPOS,
        "tipo_actual": tipo,
    }
    return render(request, "biblioteca/catalogo.html", context)

def detalle(request, libro_id):
    libro = get_object_or_404(Libro, pk=libro_id)
    resenas = libro.resenas.filter(visible=True).order_by("-fecha")

    context = {
        "libro": libro,
        "resenas": resenas,
    }
    return render(request, "biblioteca/detalle.html", context)

def resenar(request, libro_id):
    libro = get_object_or_404(Libro, pk=libro_id)

    if request.method == "POST":
        form = ResenaForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data["correo"].strip().lower()
            if libro.resenas.filter(correo=correo).exists():
                form.add_error("correo", "Ya calificaste este libro con este correo.")
            else:
                resena = form.save(commit=False)
                resena.libro = libro
                resena.save()
                return redirect("biblioteca:detalle", libro_id=libro.id)
    else:
        form = ResenaForm()

    context = {
        "libro": libro,
        "form": form,
    }
    return render(request, "biblioteca/resenar.html", context)

@require_POST
def api_recomendaciones(request):
    try:
        datos = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        datos = {}

    gustos = str(datos.get("gustos", ""))[:300]
    recomendaciones, fuente = obtener_recomendaciones(gustos)

    return JsonResponse({"recomendaciones": recomendaciones, "fuente": fuente})


def docs_api(request):
    return render(request, "biblioteca/docs_api.html")
