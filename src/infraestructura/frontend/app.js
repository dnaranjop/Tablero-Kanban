/*
 * Frontend Vanilla del Tablero Kanban Personal.
 *
 * Referencia:
 *   - TECH_CONSTRAINTS.md §1 (HTML5, CSS3, JS Vanilla ES6+).
 *   - TECH_CONSTRAINTS.md §2 (sin frameworks).
 *   - CONTEXT.md §7 (mitigación: la regla WIP NO vive solo en la interfaz).
 *
 * Decisión arquitectónica importante:
 * Este archivo NUNCA verifica si DOING tiene 3 tareas antes de enviar una
 * petición. La regla INV-01 vive en el dominio (src/dominio/tablero.py) y
 * la aplica el backend devolviendo HTTP 409. El frontend se limita a:
 *   - mostrar el tablero,
 *   - enviar las peticiones,
 *   - mostrar el mensaje de error que envie el backend.
 *
 * Si en algún momento alguien añade aquí una condición como
 *   if (columna.length) return;
 * está violando CONTEXT.md §7 y la mitigación documentada en DOMAIN.md.
 */

(function () {
  "use strict";

  const ENDPOINT_TABLERO = "/api/tablero";
  const ENDPOINT_TAREAS = "/api/tareas";

  const ESTADOS = ["TODO", "DOING", "DONE"];

  const elementos = {
    campoTitulo: document.getElementById("campo-titulo"),
    botonCrear: document.getElementById("boton-crear"),
    mensaje: document.getElementById("mensaje"),
    columnas: {
      TODO: document.getElementById("columna-TODO"),
      DOING: document.getElementById("columna-DOING"),
      DONE: document.getElementById("columna-DONE"),
    },
  };

  // ---------- Acceso a la API ----------

  async function obtenerTablero() {
    const respuesta = await fetch(ENDPOINT_TABLERO);
    if (!respuesta.ok) {
      throw new Error("No se pudo obtener el tablero.");
    }
    return await respuesta.json();
  }

  async function crearTarea(titulo) {
    const respuesta = await fetch(ENDPOINT_TAREAS, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ titulo }),
    });
    return interpretarRespuesta(respuesta);
  }

  async function moverTarea(idTarea, estadoDestino) {
    const respuesta = await fetch(`${ENDPOINT_TAREAS}/${idTarea}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ estado_destino: estadoDestino }),
    });
    return interpretarRespuesta(respuesta);
  }

  async function interpretarRespuesta(respuesta) {
    let datos = null;
    try {
      datos = await respuesta.json();
    } catch (_) {
      datos = null;
    }
    if (!respuesta.ok) {
      const mensaje = (datos && datos.error) || `Error HTTP ${respuesta.status}`;
      const error = new Error(mensaje);
      error.codigo = respuesta.status;
      throw error;
    }
    return datos;
  }

  // ---------- Renderizado ----------

  function renderizarTablero(tablero) {
    for (const estado of ESTADOS) {
      const contenedor = elementos.columnas[estado];
      contenedor.innerHTML = "";
      const tareas = tablero[estado] || [];
      for (const tarea of tareas) {
        contenedor.appendChild(crearTarjeta(tarea));
      }
    }
  }

  function crearTarjeta(tarea) {
    const li = document.createElement("li");
    li.className = "tarjeta";
    li.dataset.idTarea = tarea.id_tarea;

    const titulo = document.createElement("p");
    titulo.className = "titulo";
    titulo.textContent = tarea.titulo;
    li.appendChild(titulo);

    const acciones = document.createElement("div");
    acciones.className = "acciones";

    // Botones de transición permitidos por INV-03.
    // No verificamos WIP aquí: el backend decide.
    if (tarea.estado === "TODO") {
      acciones.appendChild(
        botonAccion("Mover a DOING", () => intentarMover(tarea.id_tarea, "DOING"))
      );
    }
    if (tarea.estado === "DOING") {
      acciones.appendChild(
        botonAccion("Mover a DONE", () => intentarMover(tarea.id_tarea, "DONE"))
      );
    }

    li.appendChild(acciones);
    return li;
  }

  function botonAccion(texto, manejador) {
    const boton = document.createElement("button");
    boton.type = "button";
    boton.textContent = texto;
    boton.addEventListener("click", manejador);
    return boton;
  }

  // ---------- Mensajes ----------

  function mostrarOk(texto) {
    elementos.mensaje.textContent = texto;
    elementos.mensaje.className = "mensaje ok";
  }

  function mostrarError(texto) {
    elementos.mensaje.textContent = texto;
    elementos.mensaje.className = "mensaje error";
  }

  function limpiarMensaje() {
    elementos.mensaje.textContent = "";
    elementos.mensaje.className = "mensaje";
  }

  // ---------- Acciones del usuario ----------

  async function intentarCrear() {
    const titulo = elementos.campoTitulo.value;
    limpiarMensaje();
    try {
      await crearTarea(titulo);
      elementos.campoTitulo.value = "";
      mostrarOk("Tarea creada.");
      await refrescar();
    } catch (error) {
      mostrarError(error.message);
    }
  }

  async function intentarMover(idTarea, estadoDestino) {
    limpiarMensaje();
    try {
      const tablero = await moverTarea(idTarea, estadoDestino);
      renderizarTablero(tablero);
      mostrarOk(`Tarea movida a ${estadoDestino}.`);
    } catch (error) {
      // Aquí caen los 409 (WIP excedido, transición inválida) y 404.
      mostrarError(error.message);
    }
  }

  async function refrescar() {
    try {
      const tablero = await obtenerTablero();
      renderizarTablero(tablero);
    } catch (error) {
      mostrarError(error.message);
    }
  }

  // ---------- Inicialización ----------

  function inicializar() {
    elementos.botonCrear.addEventListener("click", intentarCrear);
    elementos.campoTitulo.addEventListener("keydown", (evento) => {
      if (evento.key === "Enter") intentarCrear();
    });
    refrescar();
  }

  document.addEventListener("DOMContentLoaded", inicializar);
})();