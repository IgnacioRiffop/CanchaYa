document.addEventListener("DOMContentLoaded", function () {
  // 💰 Precios base
  const precios = {
    cancha: 29990, // precio fijo de la cancha
    balon: 4990,
    petos: 1000,
    conos: 1000
  };

  // 🧮 Cantidades de equipamiento
  const cantidades = {
    balon: 0,
    petos: 0,
    conos: 0
  };

  // 🔁 Cambiar cantidad de cada producto
  function cambiarCantidad(item, cambio) {
    cantidades[item] = Math.max(0, cantidades[item] + cambio);
    document.getElementById(item + "-cant").textContent = cantidades[item];
    actualizarTotales();
  }

  // 💵 Calcular totales
  function actualizarTotales() {
    // 1️⃣ Subtotal: incluye cancha + todo el equipamiento
    let subtotal = precios.cancha;
    for (let item in cantidades) {
      subtotal += cantidades[item] * precios[item];
    }

    // 2️⃣ Descuento: 20% sobre todo el subtotal
    const descuento = subtotal * 0.2;

    // 3️⃣ Total final
    const total = subtotal - descuento;

    // 4️⃣ Actualizar los elementos del DOM
    document.getElementById("subtotal").textContent = `$${subtotal.toLocaleString("es-CL")}`;
    document.getElementById("descuento").textContent = `$${descuento.toLocaleString("es-CL")}`;
    document.getElementById("total").textContent = `$${total.toLocaleString("es-CL")}`;
  }

  // ✅ Exponer la función al HTML
  window.cambiarCantidad = cambiarCantidad;

  // 🟢 Calcular totales al cargar
  actualizarTotales();
});
