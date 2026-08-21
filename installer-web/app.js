/* Buscapega — instalador web (cliente) */
(function () {
  "use strict";

  // El token viaja en la URL; se reusa en cada llamada a la API.
  var TOKEN = new URLSearchParams(location.search).get("token") || "";
  function api(path) { return path + (TOKEN ? (path.indexOf("?") >= 0 ? "&" : "?") + "token=" + encodeURIComponent(TOKEN) : ""); }

  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };

  // ── Navegación entre pasos ──────────────────────────────────────────────
  function goto(step) {
    $$(".card.step").forEach(function (c) { c.classList.toggle("hidden", c.getAttribute("data-step") !== String(step)); });
    $$("#stepbar li").forEach(function (li) {
      var n = Number(li.getAttribute("data-step"));
      li.classList.toggle("active", n === step);
      li.classList.toggle("done", n < step);
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
  $$("[data-goto]").forEach(function (b) {
    b.addEventListener("click", function () { goto(Number(b.getAttribute("data-goto"))); });
  });

  // ── Info del entorno (motor + IP) ───────────────────────────────────────
  fetch(api("/api/info")).then(function (r) { return r.json(); }).then(function (info) {
    $("#env-engine").textContent = info.engine_label || info.engine || "no detectado";
    $("#env-ip").textContent = info.ip || "—";
    window.__ip = info.ip;
  }).catch(function () {
    $("#env-engine").textContent = "—";
    $("#env-ip").textContent = "—";
  });

  // ── Mostrar campo de contraseña Gmail solo si hay correo ────────────────
  var gmail = $('input[name="gmail_user"]');
  var pwWrap = $("#gmailpw-wrap");
  gmail.addEventListener("input", function () {
    pwWrap.classList.toggle("hidden", gmail.value.trim() === "");
  });

  // ── Validación del formulario ───────────────────────────────────────────
  function clearErrors() { $$(".err").forEach(function (e) { e.textContent = ""; }); }
  function setError(field, msg) {
    var el = $('.err[data-for="' + field + '"]');
    if (el) el.textContent = msg;
  }

  function collect() {
    var f = $("#cfg");
    var phone = f.whatsapp_phone.value.replace(/\D/g, "");
    return {
      user_name: f.user_name.value.trim(),
      anthropic_api_key: f.anthropic_api_key.value.trim(),
      whatsapp_phone: phone,
      gmail_user: f.gmail_user.value.trim(),
      gmail_app_password: f.gmail_app_password.value.replace(/\s/g, ""),
      frontend_port: f.frontend_port.value.trim() || "3000",
      backend_port: f.backend_port.value.trim() || "8000"
    };
  }

  function validate(a) {
    clearErrors();
    var ok = true;
    if (a.whatsapp_phone && a.whatsapp_phone.length < 10) {
      setError("whatsapp_phone", "Debe tener al menos 10 dígitos con código de país (ej: 56912345678).");
      ok = false;
    }
    if (a.gmail_user && !/^[^@]+@[^@]+\.[^@]+$/.test(a.gmail_user)) {
      setError("gmail_user", "Formato de correo inválido. Usa correo@dominio.com o déjalo vacío.");
      ok = false;
    }
    if (a.frontend_port === a.backend_port) {
      setError("whatsapp_phone", "");
      alert("El puerto web y el del backend no pueden ser el mismo.");
      ok = false;
    }
    return ok;
  }

  // ── Consola de logs ─────────────────────────────────────────────────────
  var consoleEl = $("#console");
  function classify(line) {
    if (/^✓/.test(line)) return "l-ok";
    if (/^✗|ERROR|Falló|falló/.test(line)) return "l-err";
    if (/^!/.test(line)) return "l-warn";
    if (/^▶|^\s*▐/.test(line)) return "l-step";
    return "";
  }
  function pushLine(line) {
    var div = document.createElement("div");
    var cls = classify(line);
    if (cls) div.className = cls;
    div.textContent = line;
    consoleEl.appendChild(div);
    consoleEl.scrollTop = consoleEl.scrollHeight;
  }

  // ── Arranque de la instalación ──────────────────────────────────────────
  var startBtn = $("#startBtn");
  startBtn.addEventListener("click", function () {
    var answers = collect();
    if (!validate(answers)) return;
    window.__frontendPort = answers.frontend_port; // para armar el enlace final al app
    startBtn.disabled = true;

    fetch(api("/api/install"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(answers)
    }).then(function (r) {
      if (r.status === 409) { alert("Ya hay una instalación en curso."); return; }
      if (!r.ok) { throw new Error("HTTP " + r.status); }
      goto(3);
      streamLogs();
    }).catch(function (err) {
      startBtn.disabled = false;
      alert("No se pudo iniciar la instalación: " + err.message);
    });
  });

  function streamLogs() {
    var es = new EventSource(api("/api/stream"));
    es.addEventListener("log", function (ev) {
      try { pushLine(JSON.parse(ev.data).line); } catch (e) {}
    });
    es.addEventListener("end", function (ev) {
      es.close();
      var data = {};
      try { data = JSON.parse(ev.data); } catch (e) {}
      finish(data);
    });
    es.onerror = function () {
      // La conexión SSE puede cortarse; se reintenta sola. Si ya terminó, no importa.
    };
  }

  function finish(data) {
    var ok = data.status === "done";
    var title = $("#doneTitle");
    var msg = $("#doneMsg");
    var openApp = $("#openApp");

    if (ok) {
      title.textContent = "¡Instalación completada!";
      title.classList.remove("failed");
      msg.textContent = "Buscapega ya está corriendo en este equipo.";
      // El enlace usa el MISMO host con que abriste el instalador (localhost, IP o
      // dominio) + el puerto que elegiste: así funciona sin depender de una IP fija.
      var port = window.__frontendPort || "3000";
      openApp.href = location.protocol + "//" + location.hostname + ":" + port;
      openApp.classList.remove("hidden");
    } else {
      title.textContent = "La instalación no se completó";
      title.classList.add("failed");
      msg.textContent = "Revisa el registro de más arriba para ver qué ocurrió (código " + (data.code != null ? data.code : "?") + "). "
        + "Corrige el problema y vuelve a ejecutar el instalador.";
      openApp.classList.add("hidden");
    }
    goto(4);
  }

  // ── Finalizar (apaga el servidor del instalador) ────────────────────────
  $("#finishBtn").addEventListener("click", function () {
    fetch(api("/api/shutdown"), { method: "POST" }).catch(function () {});
    document.body.innerHTML =
      '<div class="wrap"><div class="card" style="text-align:center;margin-top:60px">'
      + '<h2>Instalador cerrado</h2><p>Ya puedes cerrar esta pestaña. '
      + 'Buscapega sigue corriendo en el servidor.</p></div></div>';
  });
})();
