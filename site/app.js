// and_Lubrifont website: type tester and character map
(function () {
  "use strict";

  var SAMPLES = {
    mk: "ТЕХНИЧКИ ОПИС\nОбјектот е со катност П+1, со армиранобетонска носива конструкција. Ѕидовите се од шуплива глинена блок-тула д = 25 см, со термоизолација од 10 см. Кота ±0,00 = 612,45 м н.в.",
    en: "TECHNICAL DESCRIPTION\nThe building has a ground floor and one upper floor, with a reinforced concrete frame. Walls: hollow clay blocks, 25 cm, with 10 cm of thermal insulation. Level ±0,00 = 612.45 m above sea level.",
    num: "0123456789\n1:50 · 1:100 · 3/8 · 5/16 · 12,5 %\n2,40 × 3,60 = 8,64 m²\nØ12/15 cm · ±0,00 · +3,15 · −0,45",
    sym: "⌀ ∅ ∆ ∡ ≅ ≈ ≠ ≤ ≥ ± ∓ × ÷ √ ∞ ° ′ ″\n← → ↑ ↓ ↔ ↕ ↺ ↻ ⇐ ⇒ ➔\n☐ ☑ ☒ ✓ ✕ ⚠ ♿ ℓ ℃ № ‰\n⏤ ⏥ ⌓ ⌒ ⌭ ⌯ ⌰ ⌱ ⌲ ⌳ ⌴ ⌵ ⌖ ⊕"
  };

  var sample = document.getElementById("sample");
  var size = document.getElementById("size");
  var sizeOut = document.getElementById("sizeOut");
  var italic = document.getElementById("italic");

  function setSample(key) {
    sample.textContent = SAMPLES[key];
  }

  function features() {
    var on = [];
    document.querySelectorAll("[data-feat]").forEach(function (box) {
      on.push('"' + box.dataset.feat + '" ' + (box.checked ? 1 : 0));
    });
    sample.style.fontFeatureSettings = on.join(", ");
    sample.style.fontKerning = document.querySelector('[data-feat="kern"]').checked ? "normal" : "none";
  }

  function segment(attr, apply) {
    document.querySelectorAll("[" + attr + "]").forEach(function (button) {
      button.addEventListener("click", function () {
        button.parentNode.querySelectorAll("button").forEach(function (b) { b.classList.remove("on"); });
        button.classList.add("on");
        apply(button.getAttribute(attr));
      });
    });
  }

  segment("data-weight", function (w) { sample.style.fontWeight = w; });
  segment("data-sample", setSample);
  italic.addEventListener("change", function () { sample.style.fontStyle = italic.checked ? "italic" : "normal"; });
  size.addEventListener("input", function () {
    sample.style.fontSize = size.value + "px";
    sizeOut.textContent = size.value + " px";
  });
  document.querySelectorAll("[data-feat]").forEach(function (box) { box.addEventListener("change", features); });
  if (window.matchMedia("(max-width: 760px)").matches) {
    size.value = 32;
    sizeOut.textContent = "32 px";
  }
  setSample("mk");
  features();

  // character map
  var groupsEl = document.getElementById("charGroups");
  var search = document.getElementById("charSearch");
  var count = document.getElementById("charCount");
  var toast = document.getElementById("toast");
  var toastTimer;
  var total = 0;

  function hex(u) { return "U+" + u.toString(16).toUpperCase().padStart(4, "0"); }

  (window.CHARS || []).forEach(function (group) {
    var section = document.createElement("div");
    section.className = "group";
    var title = document.createElement("h3");
    title.textContent = group[0];
    var grid = document.createElement("div");
    grid.className = "grid";
    group[1].forEach(function (item) {
      var ch = String.fromCodePoint(item[0]);
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = ch;
      b.title = hex(item[0]) + " " + item[1];
      b.setAttribute("aria-label", item[1] || hex(item[0]));
      b.dataset.search = (ch + " " + item[1] + " " + hex(item[0])).toLowerCase();
      grid.appendChild(b);
      total++;
    });
    section.appendChild(title);
    section.appendChild(grid);
    groupsEl.appendChild(section);
  });
  count.textContent = total + " characters";

  groupsEl.addEventListener("click", function (e) {
    var b = e.target.closest("button");
    if (!b) return;
    var done = function () { show("Copied " + b.textContent + "  " + b.title); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(b.textContent).then(done, function () { show(b.title); });
    } else {
      show(b.title);
    }
  });

  function show(text) {
    toast.textContent = text;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toast.classList.remove("show"); }, 1800);
  }

  search.addEventListener("input", function () {
    var q = search.value.trim().toLowerCase();
    var shown = 0;
    groupsEl.querySelectorAll(".group").forEach(function (section) {
      var any = false;
      section.querySelectorAll("button").forEach(function (b) {
        var hit = !q || b.dataset.search.indexOf(q) !== -1;
        b.hidden = !hit;
        if (hit) { any = true; shown++; }
      });
      section.hidden = !any;
    });
    count.textContent = q ? shown + " of " + total + " characters" : total + " characters";
  });
})();
