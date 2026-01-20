let date_selected = "today";

async function refresh_statistical( dateFilter="today") {
        const url = `/api/statistical_refresh?date=${dateFilter}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Erreur du serveur');
}
    

// Fonction pour charger les dates uniques depuis l'API
async function loadDates() {
    try {
        const response = await fetch('/api/dates_unique');
        if (!response.ok) throw new Error('Erreur du serveur');

        const dates = await response.json();

        const selectList = document.getElementById("date");


        // Ajouter les dates uniques
        for (const date of dates) {
            const option = document.createElement('option');
            option.value = date;
            option.textContent = date;
            selectList.appendChild(option);
        }


    } catch (error) {
        console.error('Erreur lors du chargement des dates :', error);
        const selectList = document.getElementById("date");
        selectList.innerHTML = '<option value="">Erreur</option>';
    }
}
// Fonction pour calculer (ex: avec la date sélectionnée)
async function refresh_date() {
    const select_list = document.getElementById("date");
    console.log("button pressed ", select_list.value);
    date_selected = document.getElementById("date").value;
    refresh_statistical("1",date_selected = date_selected);
    refresh_statistical("2",date_selected = date_selected);
}

// Attacher l'événement au bouton, si présent
const refreshBtn = document.getElementById("refresh_btn");
if (refreshBtn) {
    refreshBtn.addEventListener("click", refresh_date);
}
document.addEventListener('DOMContentLoaded', () => {
    loadDates(); // 👈 Charger les dates au chargement
});

// Actualiser toutes les 10 secondes
setInterval(() => refresh_statistical(dateFilter = date_selected), 10000);