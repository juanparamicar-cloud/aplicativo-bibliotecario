from django.urls import path
from . import views

app_name = "biblioteca"

urlpatterns = [
    path("", views.catalogo, name="catalogo"),
    path("libro/<int:libro_id>/", views.detalle, name="detalle"),
    path("libro/<int:libro_id>/resenar/", views.resenar, name="resenar"),
    path("api/recomendaciones/", views.api_recomendaciones, name="recomendaciones"),
    path("api/docs/", views.docs_api, name="docs_api"),
]
