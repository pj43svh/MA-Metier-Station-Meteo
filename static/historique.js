// Fonction pour charger les données depuis l'API Flask
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        if (!response.ok) throw new Error('Erreur du serveur');

        const data = await response.json();

        // Récupérer le tbody
        const tbody = document.getElementById('history-body');
        tbody.innerHTML = ''; // Vider le contenu existant

        // Vérifier que les listes existent
        const { date, temperature, humidite, pression, temps } = data;
        if (!date || !temperature || !humidite || !pression || !temps) {
            throw new Error('Données incomplètes reçues');
        }

        const length = Math.min(date.length, temperature.length, humidite.length, pression.length, temps.length);

        // Générer les lignes
        for (let i = length - 1; i >= 0; i--) {
            const row = document.createElement('tr');
            row.innerHTML = `
        <td>${date[i]}</td>
        <td>${temperature[i]} °C</td>
        <td>${humidite[i]} %</td>
        <td>${pression[i]} hPa</td>
        <td>${temps[i]}</td>
    `;
            tbody.appendChild(row);
        }

    } catch (error) {
        console.error('Erreur lors du chargement de l’historique :', error);
        document.getElementById('history-body').innerHTML = `<tr><td colspan="5">Erreur : ${error.message}</td></tr>`;
    }
}

// Charger les données au chargement de la page
document.addEventListener('DOMContentLoaded', loadHistory);

// Optionnel : actualiser toutes les 30 secondes
setInterval(loadHistory, 30000);