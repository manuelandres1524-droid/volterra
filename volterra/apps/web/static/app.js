(function () {
  "use strict";

  function readCookie(name) {
    var prefix = name + "=";
    var parts = document.cookie ? document.cookie.split("; ") : [];
    for (var i = 0; i < parts.length; i += 1) {
      if (parts[i].indexOf(prefix) === 0) {
        return decodeURIComponent(parts[i].slice(prefix.length));
      }
    }
    return null;
  }

  function announce(message) {
    var region = document.getElementById("live-status");
    if (!region) {
      return;
    }
    region.textContent = "";
    window.setTimeout(function () {
      region.textContent = message;
    }, 50);
  }

  // Confirmación explícita en acciones destructivas (cierre de pertenencia).
  // Usa el <dialog> nativo: el navegador ya aporta foco atrapado, capa superior
  // y cierre con Esc. El atributo `data-confirm` sigue en el HTML servido.
  var confirmDialog = document.getElementById("confirm-dialog");
  var confirmMessage = document.getElementById("confirm-dialog-message");
  var confirmAccept = document.getElementById("confirm-dialog-accept");
  var pendingForm = null;
  var bypassForm = null;

  document.addEventListener(
    "submit",
    function (event) {
      var form = event.target;
      if (!form || typeof form.getAttribute !== "function") {
        return;
      }
      if (form === bypassForm) {
        bypassForm = null;
        return;
      }
      var message = form.getAttribute("data-confirm");
      if (!message) {
        return;
      }
      event.preventDefault();
      event.stopImmediatePropagation();

      if (!confirmDialog || typeof confirmDialog.showModal !== "function") {
        if (window.confirm(message)) {
          if (form.requestSubmit) {
            bypassForm = form;
            form.requestSubmit();
          } else {
            form.submit();
          }
        }
        return;
      }

      pendingForm = form;
      confirmMessage.textContent = message;
      confirmAccept.textContent = form.getAttribute("data-confirm-action") || "Confirmar";
      confirmDialog.returnValue = "";
      confirmDialog.showModal();
    },
    true
  );

  if (confirmDialog) {
    confirmDialog.addEventListener("close", function () {
      var form = pendingForm;
      pendingForm = null;
      if (!form || confirmDialog.returnValue !== "confirm") {
        return;
      }
      if (form.requestSubmit) {
        bypassForm = form;
        form.requestSubmit();
      } else {
        form.submit();
      }
    });
  }

  // Si requestSubmit() no llega a disparar submit (validación nativa fallida),
  // el formulario no debe quedar marcado como ya confirmado.
  document.addEventListener(
    "invalid",
    function () {
      bypassForm = null;
    },
    true
  );

  // HTMX: estado ocupado y errores sin sustituir la página por una respuesta
  // de error completa. La autorización sigue en el servidor.
  document.body.addEventListener("htmx:beforeRequest", function () {
    var panel = document.getElementById("members-panel");
    if (panel) {
      panel.setAttribute("aria-busy", "true");
    }
  });

  document.body.addEventListener("htmx:afterRequest", function () {
    var panel = document.getElementById("members-panel");
    if (panel) {
      panel.removeAttribute("aria-busy");
    }
  });

  document.body.addEventListener("htmx:afterSwap", function () {
    announce("Lista actualizada.");
  });

  document.body.addEventListener("htmx:beforeSwap", function (event) {
    var status = event.detail && event.detail.xhr ? event.detail.xhr.status : 0;
    if (status === 401) {
      event.detail.shouldSwap = false;
      window.location.assign("/login");
      return;
    }
    if (status >= 400) {
      event.detail.shouldSwap = false;
      announce("No se pudo actualizar la lista. Recarga la página e inténtalo de nuevo.");
    }
  });

  // Renovación silenciosa de la sesión antes de que caduque el access token.
  var csrf = readCookie("volterra_csrf");
  if (!csrf) {
    return;
  }

  var intervalMs = 45 * 60 * 1000;

  function refresh() {
    fetch("/auth/refresh", {
      method: "POST",
      headers: { "X-CSRF-Token": csrf },
      credentials: "same-origin",
    })
      .then(function (response) {
        if (response.status === 401) {
          window.location.assign("/login");
        }
      })
      .catch(function () {
        // Sin red no se fuerza el cierre de sesión: la siguiente navegación decide.
      });
  }

  window.setTimeout(function () {
    refresh();
    window.setInterval(refresh, intervalMs);
  }, intervalMs);
})();
