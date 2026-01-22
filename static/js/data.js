/**
 * Station Meteo - Dashboard JavaScript
 *
 * Gere l'affichage dynamique des capteurs.
 * Supporte un nombre illimite de capteurs.
 */

// Conteneur pour les capteurs
const sensorsContainer = document.querySelector('.content');

/**
 * Cree le HTML pour un capteur
 */
function createSensorCard(sensorNum) {
    const card = document.createElement('div');
    card.className = 'sensors';
    card.id = `sensor${sensorNum}`;

    card.innerHTML = `
        <h1>Sensor ${sensorNum}</h1>

        <div class="data">
            <h2>Temperature :</h2>
            <p id="temperature${sensorNum}">-- °C</p>
        </div>

        <div class="data">
            <h2>Pressure :</h2>
            <p id="pressure${sensorNum}">-- hPa</p>
        </div>

        <div class="data">
            <h2>Humidity level :</h2>
            <p id="humidity${sensorNum}">-- %</p>
        </div>
    `;

    return card;
}

/**
 * Charge la liste des capteurs et cree les cartes
 */
async function loadSensors() {
    try {
        const response = await fetch('/api/sensors');
        const data = await response.json();

        // Vider le conteneur
        sensorsContainer.innerHTML = '';

        if (data.sensors && data.sensors.length > 0) {
            // Creer une carte pour chaque capteur
            data.sensors.forEach(sensor => {
                const sensorNum = sensor.replace('esp', '');
                const card = createSensorCard(sensorNum);
                sensorsContainer.appendChild(card);
            });
        } else {
            // Aucun capteur trouve
            sensorsContainer.innerHTML = `
                <div class="no-sensors">
                    <h2>Aucun capteur detecte</h2>
                    <p>En attente de donnees des ESP32...</p>
                </div>
            `;
        }

        // Mettre a jour les donnees
        updateData();

    } catch (error) {
        console.error('Erreur chargement capteurs:', error);
        // Fallback: afficher 2 capteurs par defaut
        sensorsContainer.innerHTML = '';
        sensorsContainer.appendChild(createSensorCard(1));
        sensorsContainer.appendChild(createSensorCard(2));
        updateDataLegacy();
    }
}

/**
 * Met a jour les donnees de tous les capteurs (nouvelle API)
 */
async function updateData() {
    try {
        const response = await fetch('/api/all/latest');
        const data = await response.json();

        // Mettre a jour chaque capteur
        for (const [sensor, values] of Object.entries(data)) {
            const sensorNum = sensor.replace('esp', '');

            // Temperature
            const tempEl = document.getElementById(`temperature${sensorNum}`);
            if (tempEl) {
                tempEl.textContent = values.temperature !== null
                    ? `${values.temperature.toFixed(1)} °C`
                    : '-- °C';
            }

            // Pression
            const pressEl = document.getElementById(`pressure${sensorNum}`);
            if (pressEl) {
                pressEl.textContent = values.pressure !== null
                    ? `${values.pressure.toFixed(1)} hPa`
                    : '-- hPa';
            }

            // Humidite
            const humEl = document.getElementById(`humidity${sensorNum}`);
            if (humEl) {
                humEl.textContent = values.humidity !== null
                    ? `${values.humidity.toFixed(1)} %`
                    : '-- %';
            }
        }
    } catch (error) {
        console.error('Erreur mise a jour:', error);
        // Fallback vers l'ancienne API
        updateDataLegacy();
    }
}

/**
 * Ancienne methode de mise a jour (compatibilite)
 */
function updateDataLegacy() {
    // Capteur 1
    fetch('/api/temperature1')
        .then(response => response.text())
        .then(text => {
            const el = document.getElementById('temperature1');
            if (el) el.textContent = (text === "NULL" || text === "Aucune donnée") ? '-- °C' : text + ' °C';
        });

    fetch('/api/pressure1')
        .then(response => response.text())
        .then(text => {
            const el = document.getElementById('pressure1');
            if (el) el.textContent = (text === "NULL" || text === "Aucune donnée") ? '-- hPa' : text + ' hPa';
        });

    fetch('/api/humidity1')
        .then(response => response.text())
        .then(text => {
            const el = document.getElementById('humidity1');
            if (el) el.textContent = (text === "NULL" || text === "Aucune donnée") ? '-- %' : text + ' %';
        });

    // Capteur 2
    fetch('/api/temperature2')
        .then(response => response.text())
        .then(text => {
            const el = document.getElementById('temperature2');
            if (el) el.textContent = (text === "NULL" || text === "Aucune donnée") ? '-- °C' : text + ' °C';
        });

    fetch('/api/pressure2')
        .then(response => response.text())
        .then(text => {
            const el = document.getElementById('pressure2');
            if (el) el.textContent = (text === "NULL" || text === "Aucune donnée") ? '-- hPa' : text + ' hPa';
        });

    fetch('/api/humidity2')
        .then(response => response.text())
        .then(text => {
            const el = document.getElementById('humidity2');
            if (el) el.textContent = (text === "NULL" || text === "Aucune donnée") ? '-- %' : text + ' %';
        });
}

// Charger les capteurs au demarrage
loadSensors();

// Recharger la liste des capteurs toutes les 60 secondes (pour detecter nouveaux capteurs)
setInterval(loadSensors, 60000);

// Mettre a jour les donnees toutes les 20 secondes
setInterval(updateData, 20000);
