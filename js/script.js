/* ============================================================
   AI Resume Screening System – Frontend Script
   ============================================================ */

document.addEventListener("DOMContentLoaded", () => {
  initFlashToasts();
  initDropZone();
  initSidebarToggle();
  initDashboardCharts();
  initMatchProgressBars();
  initFileNameDisplay();
});

/* ---- Flash toast auto-dismiss ---- */
function initFlashToasts() {
  document.querySelectorAll(".flash-toast").forEach((el) => {
    setTimeout(() => {
      el.style.transition = "opacity 0.4s";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 400);
    }, 4500);
  });
}

/* ---- Drag-and-drop upload zone ---- */
function initDropZone() {
  const zone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("resumes");
  if (!zone || !fileInput) return;

  zone.addEventListener("click", () => fileInput.click());

  zone.addEventListener("dragover", (e) => {
    e.preventDefault();
    zone.classList.add("drag-over");
  });

  zone.addEventListener("dragleave", () => zone.classList.remove("drag-over"));

  zone.addEventListener("drop", (e) => {
    e.preventDefault();
    zone.classList.remove("drag-over");
    const dt = e.dataTransfer;
    if (dt && dt.files.length) {
      fileInput.files = dt.files;
      updateDropZoneLabel(fileInput.files);
    }
  });

  fileInput.addEventListener("change", () => updateDropZoneLabel(fileInput.files));
}

function updateDropZoneLabel(files) {
  const label = document.getElementById("drop-zone-label");
  if (!label) return;
  if (files.length === 0) {
    label.textContent = "Drag & drop resumes here, or click to browse";
  } else if (files.length === 1) {
    label.textContent = `Selected: ${files[0].name}`;
  } else {
    label.textContent = `${files.length} files selected`;
  }
}

/* ---- Show selected JD file name ---- */
function initFileNameDisplay() {
  const jdFile = document.getElementById("jd_file");
  if (!jdFile) return;
  jdFile.addEventListener("change", () => {
    const label = document.getElementById("jd-file-label");
    if (label && jdFile.files.length) {
      label.textContent = jdFile.files[0].name;
    }
  });
}

/* ---- Sidebar mobile toggle ---- */
function initSidebarToggle() {
  const toggleBtn = document.getElementById("sidebar-toggle");
  const sidebar = document.querySelector(".sidebar");
  if (!toggleBtn || !sidebar) return;
  toggleBtn.addEventListener("click", () => sidebar.classList.toggle("open"));
}

/* ---- Animate match progress bars ---- */
function initMatchProgressBars() {
  document.querySelectorAll(".match-progress-bar").forEach((bar) => {
    const target = parseFloat(bar.dataset.score || 0);
    bar.style.width = "0%";
    setTimeout(() => {
      bar.style.width = Math.min(target, 100) + "%";
    }, 150);
  });
}

/* ---- Dashboard charts ---- */
function initDashboardCharts() {
  buildMatchChart();
  buildSkillsChart();
}

function buildMatchChart() {
  const canvas = document.getElementById("matchChart");
  if (!canvas) return;

  const labels = JSON.parse(canvas.dataset.labels || "[]");
  const scores = JSON.parse(canvas.dataset.scores || "[]");

  new Chart(canvas, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Match Score (%)",
        data: scores,
        backgroundColor: "rgba(67,97,238,0.75)",
        borderColor: "#4361ee",
        borderWidth: 2,
        borderRadius: 6,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.parsed.y.toFixed(1)}%`,
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: { callback: (v) => v + "%" },
          grid: { color: "#f0f0f0" },
        },
        x: { grid: { display: false } },
      },
    },
  });
}

function buildSkillsChart() {
  const canvas = document.getElementById("skillsChart");
  if (!canvas) return;

  const labels = JSON.parse(canvas.dataset.labels || "[]");
  const counts = JSON.parse(canvas.dataset.counts || "[]");

  const palette = [
    "#4361ee","#4cc9f0","#06d6a0","#f9c74f",
    "#ef233c","#3a0ca3","#7209b7","#480ca8",
  ];

  new Chart(canvas, {
    type: "doughnut",
    data: {
      labels,
      datasets: [{
        data: counts,
        backgroundColor: palette,
        borderWidth: 2,
        borderColor: "#fff",
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "right",
          labels: { boxWidth: 12, font: { size: 11 } },
        },
      },
      cutout: "62%",
    },
  });
}

/* ---- Confirm delete ---- */
function confirmDelete(form) {
  if (confirm("Remove this candidate from the system?")) {
    form.submit();
  }
}
