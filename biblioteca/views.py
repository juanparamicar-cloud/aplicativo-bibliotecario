from django.shortcuts import render ,get_object_or_404 , redirect
from django.db.models import Avg, Count, Q
from .forms import ResenaForm
from .models import Libro,Resena

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
