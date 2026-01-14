// ----- MENU -----
const menuItems = document.querySelectorAll(".sidebar li");
const pages = document.querySelectorAll(".page");

menuItems.forEach(item => {
  item.addEventListener("click", () => {
    menuItems.forEach(i => i.classList.remove("active"));
    pages.forEach(p => p.classList.remove("active"));

    item.classList.add("active");

    const pageId = item.getAttribute("data-page");
    if (!pageId) return; // sécurité

    const target = document.getElementById(pageId);
    if (target) target.classList.add("active");
  });
});

// ----- DATA -----
function updateData() {
  fetch("/data")
    .then(r => r.json())
    .then(data => {
      document.getElementById("temp").textContent = data.temperature + " °C";
      document.getElementById("hum").textContent = data.humidity + " %";
      document.getElementById("press").textContent = data.pressure + " hPa";
      document.getElementById("time").textContent = data.time;
    })
    .catch(() => console.log("En attente des données..."));
}

updateData();
setInterval(updateData, 5000);

// ----- ACCORDION (À propos) -----
const accordionHeaders = document.querySelectorAll(".accordion-header");

accordionHeaders.forEach(header => {
  header.addEventListener("click", () => {
    const content = header.nextElementSibling;
    content.classList.toggle("open");
  });
});

// ----- HISTORIQUE -----
const historyBody = document.getElementById("history-body");

function addToHistory(data) {
  if (!historyBody) return;

  const row = document.createElement("tr");

  row.innerHTML = `
    <td>${data.date}</td>
    <td>${data.time}</td>
    <td>${data.temperature}</td>
    <td>${data.humidity}</td>
    <td>${data.pressure}</td>
  `;

  historyBody.prepend(row); // dernière mesure en haut
}

//const menuToggle = document.getElementById("menuToggle");
const sidebar = document.querySelector(".sidebar");
const app = document.querySelector(".app");

menuToggle.addEventListener("click", () => {
  sidebar.classList.toggle("open");
  app.classList.toggle("menu-open");
});





