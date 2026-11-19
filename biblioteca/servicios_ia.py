import json
import urllib.request

from django.conf import settings
from django.db.models import Avg, Count, Q
from django.urls import reverse

from .models import Libro

PUNTAJE_MINIMO = 3.5
MAX_LIBROS_A_LA_IA = 10


def libros_mejor_puntuados():
    visibles = Q(resenas__visible=True)
    return list(
        Libro.objects.annotate(
            prom=Avg("resenas__puntuacion", filter=visibles),
            total=Count("resenas", filter=visibles),
        )
        .filter(total__gte=1, prom__gte=PUNTAJE_MINIMO)
        .order_by("-prom", "-total")[:MAX_LIBROS_A_LA_IA]
    )


def armar_catalogo(libros):
    catalogo = []
    for libro in libros:
        comentarios = (
            libro.resenas.filter(visible=True)
            .order_by("-fecha")
            .values_list("comentario", flat=True)[:3]
        )
        catalogo.append({
            "id": libro.id,
            "nombre": libro.nombre,
            "autor": libro.autor,
            "tipo": libro.get_tipo_display(),
            "promedio": round(libro.prom, 1),
            "total_resenas": libro.total,
            "comentarios": [c[:200] for c in comentarios],
        })
    return catalogo


def pedir_al_servicio_ia(catalogo, gustos):
    datos = json.dumps({"catalogo": catalogo, "gustos": gustos}).encode("utf-8")
    peticion = urllib.request.Request(
        settings.SERVICIO_IA_URL.rstrip("/") + "/recomendar",
        data=datos,
        headers={
            "Content-Type": "application/json",
            "X-Servicio-Token": settings.SERVICIO_IA_TOKEN,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(peticion, timeout=25) as respuesta:
            return json.loads(respuesta.read()).get("recomendaciones", [])
    except Exception as error:
        print(f"[servicio IA] no disponible: {error}")
        return []


def a_diccionario(libro, motivo):
    return {
        "id": libro.id,
        "nombre": libro.nombre,
        "autor": libro.autor,
        "tipo": libro.get_tipo_display(),
        "promedio": round(libro.prom, 1),
        "total_resenas": libro.total,
        "motivo": motivo,
        "url": reverse("biblioteca:detalle", args=[libro.id]),
    }


def obtener_recomendaciones(gustos=""):
    libros = libros_mejor_puntuados()
    if not libros:
        return [], "sin_datos"

    por_id = {libro.id: libro for libro in libros}
    respuesta_ia = pedir_al_servicio_ia(armar_catalogo(libros), gustos)

    resultado = []
    for item in respuesta_ia:
        try:
            libro = por_id.get(int(item.get("id")))
        except (TypeError, ValueError):
            continue
        if libro and all(r["id"] != libro.id for r in resultado):
            resultado.append(a_diccionario(libro, item.get("motivo", "")))

    if resultado:
        return resultado[:3], "ia"

    respaldo = [
        a_diccionario(libro, "Uno de los libros mejor calificados por la comunidad.")
        for libro in libros[:3]
    ]
    return respaldo, "puntaje"
