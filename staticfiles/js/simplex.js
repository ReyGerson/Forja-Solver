//Script para el método Simplex
const agregarRestricciones = document.getElementById("agregarRestricciones");
const quitarRestricciones = document.getElementById("quitarRestricciones");
const listaRestricciones = document.getElementById("listaRestricciones");
const tipoObjetivo = document.getElementById("tipo_objetivo");
const textoObjetivo = document.getElementById("texto_objetivo");

let numRestricciones = 0;

// Actualizar texto del objetivo cuando cambia la selección
tipoObjetivo.addEventListener("change", function() {
  const tipo = this.value;
  textoObjetivo.textContent = tipo + " Z = ";
});

function getPlaceholderRestriction() {
  return tipoObjetivo.value === "Maximizar" ? "x_{1} + x_{2} \\leq 8" : "x_{1} + x_{2} \\geq 8";
}

agregarRestricciones.addEventListener("click", (e) => {
  e.preventDefault();

  numRestricciones++;

  // Crear el campo math-field para la restricción
  const mathLive = document.createElement("math-field");
  mathLive.id = `restriccion${numRestricciones}`;
  mathLive.style.cssText = "display: inline-block; width: 400px; margin: 5px;";
  
  // Agregar placeholder según el tipo de objetivo
  mathLive.value = getPlaceholderRestriction();

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
  
  // Obtener valores de las restricciones
  const valores = Array.from(lista).map((el) => {
    const valor = el.getValue("latex");
    return valor || "";
  }).filter(v => v.trim() !== ""); // Filtrar restricciones vacías
  
  if (valores.length === 0) {
    alert("Por favor, complete al menos una restricción.");
    e.preventDefault();
    return;
  }
  
  // Validar coherencia entre tipo de objetivo y restricciones
  const tipoSeleccionado = tipoObjetivo.value;
  let errorValidacion = false;
  let mensajeError = "";
  
  if (tipoSeleccionado === "Maximizar") {
    // Para maximizar, solo se permiten restricciones con <=
    for (let restriccion of valores) {
      if (restriccion.includes("\\geq") || restriccion.includes("\\ge") || restriccion.includes(">")) {
        errorValidacion = true;
        mensajeError = "⚠️ MÉTODO SIMPLEX ESTÁNDAR NO APLICABLE\n\n" +
                      "Para problemas de MAXIMIZACIÓN solo se permiten restricciones del tipo ≤ (menor o igual).\n\n" +
                      "💡 SOLUCIÓN: Para restricciones ≥ debe aplicar el Método de la Gran M o Método de las Dos Fases.";
        break;
      }
    }
  } else {
    // Para minimizar, advertir sobre las limitaciones
    errorValidacion = true;
    mensajeError = "⚠️ PROBLEMA DE MINIMIZACIÓN DETECTADO\n\n" +
                  "Los problemas de MINIMIZACIÓN requieren métodos avanzados que actualmente tienen limitaciones en este sistema.\n\n" +
                  "💡 RECOMENDACIONES:\n" +
                  "• Use el Método de las Dos Fases\n" +
                  "• Use el Método de la Gran M\n" +
                  "• Convierta manualmente a maximización\n\n" +
                  "¿Desea continuar de todas formas?\n" +
                  "(El resultado puede no ser correcto)";
    
    // Permitir continuar con confirmación
    if (confirm(mensajeError + "\n\nPresione OK para continuar o Cancelar para modificar el problema.")) {
      errorValidacion = false; // Permitir continuar
    }
  }
  
  if (errorValidacion) {
    alert(mensajeError);
    e.preventDefault();
    return;
  }
  
  // Si pasa todas las validaciones, enviar el formulario
  campoFuncionHidden.value = funcionValue;
  restriccionesHidden.value = JSON.stringify(valores);
});
