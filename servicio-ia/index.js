const express = require("express");
const swaggerUi = require("swagger-ui-express");
const documentacion = require("./openapi.json");

const app = express();
app.use(express.json({ limit: "200kb" }));
app.use("/docs", swaggerUi.serve, swaggerUi.setup(documentacion));

const PUERTO = process.env.PORT || 3000;
const TOKEN = process.env.SERVICIO_IA_TOKEN || "";
const API_KEY = process.env.IA_API_KEY || "";
const MODELO = process.env.IA_MODELO || "gemini-flash-latest";
const MODELOS = [MODELO, process.env.IA_MODELO_RESPALDO || "gemini-flash-lite-latest"];


app.get("/salud", (req, res) => {
  res.json({ estado: "ok" });
});

app.post("/recomendar", async (req, res) => {
  if (TOKEN && req.get("X-Servicio-Token") !== TOKEN) {
    return res.status(401).json({ error: "No autorizado" });
  }

  const { catalogo, gustos } = req.body || {};
  if (!Array.isArray(catalogo) || catalogo.length === 0) {
    return res.status(400).json({ error: "Falta el catálogo de libros" });
  }

  if (!API_KEY) {
    console.log("⚠️ No hay IA_API_KEY: respondo lista vacía");
    return res.json({ recomendaciones: [], aviso: "Servicio sin clave de IA" });
  }

  try {
    const recomendaciones = await pedirAGemini(catalogo, gustos || "");
    res.json({ recomendaciones });
  } catch (error) {
    console.error("Error con la IA:", error.message);
    res.json({ recomendaciones: [] });
  }
});

function armarPrompt(catalogo, gustos) {
  return `Eres el bibliotecario de la Universidad Uninpahu.
Estos son los libros MEJOR CALIFICADOS por la comunidad, con su puntaje promedio (1 a 5) y algunos comentarios de lectores:

${JSON.stringify(catalogo, null, 2)}

${gustos ? `El visitante dice que busca: "${gustos}".` : "El visitante no indicó preferencias."}

Elige máximo 3 libros SOLO de esta lista. Da prioridad al puntaje más alto y, si el visitante indicó preferencias, a los que mejor encajen con ellas.
Para cada uno escribe un motivo en español de máximo 25 palabras, basado en el puntaje y en lo que dicen los comentarios.
Responde ÚNICAMENTE con JSON con este formato:
[{"id": 1, "motivo": "..."}]`;
}



async function pedirAGemini(catalogo, gustos) {
  let ultimoError;

  for (const modelo of MODELOS) {
    try {
      return await llamarModelo(modelo, catalogo, gustos);
    } catch (error) {
      console.error(`Falló ${modelo}:`, error.message);
      ultimoError = error;
    }
  }
  throw ultimoError;
}

async function llamarModelo(modelo, catalogo, gustos) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${modelo}:generateContent`;

  const respuesta = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-goog-api-key": API_KEY },
    body: JSON.stringify({
      contents: [{ parts: [{ text: armarPrompt(catalogo, gustos) }] }],
       generationConfig: {
        temperature: 0.3,
        responseMimeType: "application/json",
        ...(modelo.includes("lite") ? {} : { thinkingConfig: { thinkingBudget: 0 } }),
      },
    }),
    signal: AbortSignal.timeout(10000),
  });

  if (!respuesta.ok) {
    const detalle = await respuesta.text();
    throw new Error(`Gemini respondió ${respuesta.status}: ${detalle}`);
  }

  const datos = await respuesta.json();
  const texto = datos?.candidates?.[0]?.content?.parts?.[0]?.text || "[]";
  console.log(`Respuesta de Gemini (${modelo}):`, texto);

  let lista = JSON.parse(texto);
  if (!Array.isArray(lista)) lista = lista.recomendaciones || [];

  const idsValidos = new Set(catalogo.map((libro) => libro.id));
  return lista
    .filter((item) => idsValidos.has(Number(item.id)))
    .slice(0, 3)
    .map((item) => ({ id: Number(item.id), motivo: String(item.motivo || "") }));
}

app.listen(PUERTO, () => {
  console.log(`Servicio de IA escuchando en el puerto ${PUERTO}`);
});
