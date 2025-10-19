document.addEventListener("DOMContentLoaded", function () {
  // 💰 Precios base
  const precios = {
    cancha: 29990, // precio fijo de la cancha
    balon: 4990,
    petos: 1000,
    conos: 1000
  };

  // 🧮 Cantidades de cada equipamiento
  const cantidades = {
    balon: 0,
    petos: 0,
    conos: 0
  };

  // 🔁 Cambia la cantidad según el botón
  function cambiarCantidad(item, cambio) {
    cantidades[item] = Math.max(0, cantidades[item] + cambio);
    document.getElementById(item + "-cant").textContent = cantidades[item];
    actualizarTotales();
  }

  // 💵 Calcula los totales
  function actualizarTotales() {
    // El subtotal parte con el precio de la cancha
    let subtotal = precios.cancha;

    // Suma el equipamiento adicional
    for (let item in cantidades) {
      subtotal += cantidades[item] * precios[item];
    }

    // Calcula el descuento (si aplica)
    const descuento = subtotal > precios.cancha ? (subtotal - precios.cancha) * 0.2 : 0;
    const total = subtotal - descuento;

    // Muestra los valores formateados
    document.getElementById("subtotal").textContent = `$${subtotal.toLocaleString("es-CL")}`;
    document.getElementById("descuento").textContent = `$${descuento.toLocaleString("es-CL")}`;
    document.getElementById("total").textContent = `$${total.toLocaleString("es-CL")}`;
  }

  // ✅ Deja disponible la función para los botones del HTML
  window.cambiarCantidad = cambiarCantidad;

  // 🟢 Muestra el precio base desde el inicio
  actualizarTotales();
});
