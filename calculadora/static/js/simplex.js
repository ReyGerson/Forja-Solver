//Script para el método Simplex
const agregarRestricciones = document.getElementById("agregarRestricciones");
const quitarRestricciones = document.getElementById("quitarRestricciones");
const listaRestricciones = document.getElementById("listaRestricciones");

let numRestricciones = 0;

agregarRestricciones.addEventListener("click", (e) => {
  e.preventDefault();

  numRestricciones++;

  // Crear el campo math-field para la restricción
  const mathLive = document.createElement("math-field");
  mathLive.id = `restriccion${numRestricciones}`;
  mathLive.style.cssText = "display: inline-block; width: 400px; margin: 5px;";
  
  // Agregar placeholder para ayudar al usuario
  mathLive.value = "x_{1} + x_{2} \\leq 0";

  const li = document.createElement("li");
  li.id = `itemRestriccion${numRestricciones}`;
  li.style.cssText = "margin: 10px 0; padding: 10px; background: #f0f0f0; border-radius: 5px;";
  
  // Agregar etiqueta
  const label = document.createElement("span");
  label.textContent = `Restricción ${numRestricciones}: `;
  label.style.fontWeight = "bold";
  
  li.appendChild(label);
  li.appendChild(mathLive);

  listaRestricciones.appendChild(li);
  
  // Enfocar el nuevo campo
  setTimeout(() => {
    mathLive.focus();
    mathLive.select();
  }, 100);
});

quitarRestricciones.addEventListener("click", (e) => {
  e.preventDefault();
  if (numRestricciones > 0) {
    const liToRemove = document.getElementById(
      `itemRestriccion${numRestricciones}`
    );
    if (liToRemove) {
      liToRemove.remove();
      numRestricciones--;
    }
  }
});

// Manejo del envío del formulario
const campoFuncion = document.getElementById("campoFuncionObjetivo");
const campoFuncionHidden = document.getElementById("funcion_objetivo_hidden");
const restriccionesHidden = document.getElementById("restricciones_hidden");

document.querySelector("form").addEventListener("submit", function (e) {
  // Validar que hay función objetivo
  const funcionValue = campoFuncion.getValue("latex");
  if (!funcionValue || funcionValue.trim() === "") {
    alert("Por favor, ingrese la función objetivo.");
    e.preventDefault();
    return;
  }
  
  // Validar que hay al menos una restricción
  const lista = document.querySelectorAll("#listaRestricciones math-field");
  if (lista.length === 0) {
    alert("Por favor, agregue al menos una restricción.");
    e.preventDefault();
    return;
  }
  
  // Obtener valores
  campoFuncionHidden.value = funcionValue;
  
  const valores = Array.from(lista).map((el) => {
    const valor = el.getValue("latex");
    return valor || "";
  }).filter(v => v.trim() !== ""); // Filtrar restricciones vacías
  
  if (valores.length === 0) {
    alert("Por favor, complete al menos una restricción.");
    e.preventDefault();
    return;
  }
  
  restriccionesHidden.value = JSON.stringify(valores);
});
