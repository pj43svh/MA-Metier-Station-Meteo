// Fonction pour récupérer les données résumées d'un capteur
function fetchSummary(sensorId) {
    fetch(`/daily_summary?sensor_id=${sensorId}&limit=999`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur réseau pour capteur ${sensorId}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.length === 0) {
                console.log(`Aucune donnée pour capteur ${sensorId}`);
                return;
            }

            const day = data[0];

            // Mettre à jour les éléments HTML
            document.getElementById(`date${sensorId}`).textContent = day.date;
            document.getElementById(`temp-max${sensorId}`).textContent = day.temperature.max !== null ? day.temperature.max : "—";
            document.getElementById(`temp-min${sensorId}`).textContent = day.temperature.min !== null ? day.temperature.min : "—";
            document.getElementById(`hum-max${sensorId}`).textContent = day.humidity.max !== null ? day.humidity.max : "—";
            document.getElementById(`hum-min${sensorId}`).textContent = day.humidity.min !== null ? day.humidity.min : "—";
            document.getElementById(`press-max${sensorId}`).textContent = day.pressure.max !== null ? day.pressure.max : "—";
            document.getElementById(`press-min${sensorId}`).textContent = day.pressure.min !== null ? day.pressure.min : "—";
        })
        .catch(err => {
            console.error(`Erreur lors de la récupération des données du capteur ${sensorId} :`, err);
            document.getElementById(`date${sensorId}`).textContent = "Erreur";
        });
}

// Appeler les deux capteurs au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    fetchSummary(1);
    fetchSummary(2);
});