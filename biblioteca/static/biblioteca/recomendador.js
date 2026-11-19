document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("modalRecomendador");
  const formulario = document.getElementById("formRecomendador");
  const contenedor = document.getElementById("resultadosRecomendador");
  const url = modal.dataset.url;
  let yaCargo = false;

  modal.addEventListener("show.bs.modal", () => {
    if (!yaCargo) {
      pedirRecomendaciones("");
      yaCargo = true;
    }
  });

  formulario.addEventListener("submit", (evento) => {
    evento.preventDefault();
    pedirRecomendaciones(formulario.gustos.value.trim());
  });

  async function pedirRecomendaciones(gustos) {
    contenedor.innerHTML =
      '<div class="text-center py-4"><div class="spinner-border text-primary"></div>' +
      '<p class="mt-2 text-muted">Buscando los mejores libros para ti…</p></div>';

    try {
      const respuesta = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": formulario.csrfmiddlewaretoken.value,
        },
        body: JSON.stringify({ gustos }),
      });
      if (!respuesta.ok) throw new Error(respuesta.status);
      const datos = await respuesta.json();
      mostrar(datos.recomendaciones, datos.fuente);
    } catch (error) {
      contenedor.innerHTML =
        '<p class="text-danger">No pudimos cargar las recomendaciones. Intenta de nuevo.</p>';
    }
  }

  function mostrar(libros, fuente) {
    contenedor.innerHTML = "";

    if (!libros.length) {
      contenedor.innerHTML =
        '<p class="text-muted">Todavía no hay libros con suficientes reseñas para recomendar.</p>';
      return;
    }

    libros.forEach((libro) => {
      const tarjeta = document.createElement("a");
      tarjeta.href = libro.url;
      tarjeta.className = "card mb-2 text-decoration-none text-body";

      const cuerpo = document.createElement("div");
      cuerpo.className = "card-body py-2";

      const titulo = document.createElement("div");
      titulo.className = "d-flex justify-content-between";
      const nombre = document.createElement("strong");
      nombre.textContent = libro.nombre;
      const estrellas = document.createElement("span");
      estrellas.className = "badge text-bg-warning";
      estrellas.textContent = `⭐ ${libro.promedio} (${libro.total_resenas})`;
      titulo.append(nombre, estrellas);

      const autor = document.createElement("small");
      autor.className = "text-muted d-block";
      autor.textContent = `${libro.autor} · ${libro.tipo}`;

      const motivo = document.createElement("p");
      motivo.className = "mb-0 mt-1 small";
      motivo.textContent = libro.motivo;

      cuerpo.append(titulo, autor, motivo);
      tarjeta.append(cuerpo);
      contenedor.append(tarjeta);
    });

    if (fuente === "puntaje") {
      const aviso = document.createElement("p");
      aviso.className = "text-muted small mt-2 mb-0";
      aviso.textContent = "El asistente de IA no está disponible; te mostramos los mejor calificados.";
      contenedor.append(aviso);
    }
  }
});
