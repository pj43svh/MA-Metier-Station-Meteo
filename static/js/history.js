// Fonction pour charger les données depuis l'API Flask
async function loadHistory(sensorId) {
    try {
        const response = await fetch(`/api/history${sensorId}`);
        if (!response.ok) throw new Error('Erreur du serveur');

        const data = await response.json();

        // Vérifier que les listes existent
        const { date, hour, temperature, humidity, pressure } = data;
        if (!date ||!hour || !temperature || !humidity || !pressure) {
            throw new Error('Données incomplètes reçues');
        }

        const maxLength = Math.max(date.length,hour.length, temperature.length, humidity.length, pressure.length);
        const tbody = document.getElementById(`history${sensorId}-body`);
        tbody.innerHTML = ''; // Vider le contenu existant
        // Générer les lignes
        for (let i = maxLength - 1; i >= 0; i--) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${date[i] !== undefined ? date[i] : '—'}</td>
                <td>${hour[i] !== undefined ? hour[i] : '—'}</td>
                <td>${temperature[i] !== undefined ? temperature[i] + ' °C' : '—'}</td>
                <td>${humidity[i] !== undefined ? humidity[i] + ' %' : '—'}</td>
                <td>${pressure[i] !== undefined ? pressure[i] + ' hPa' : '—'}</td>
                `;
            tbody.appendChild(row);
        }

    } catch (error) {
        console.error('Erreur lors du chargement de l’historique :', error);
        document.getElementById(`history${sensorId}-body`).innerHTML = `< tr > <td colspan="4">Erreur : ${error.message}</td></tr > `;
    }
}




// Optionnel : actualiser toutes les 30 secondes
setInterval(loadHistory("1"), 30000);
setInterval(loadHistory("2"), 30000);