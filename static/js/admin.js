/**
 * Station Meteo - Admin Panel JavaScript
 * Gestion des ESP32 connectes
 */

const devicesContainer = document.getElementById('devices-container');

/**
 * Charge la liste des ESP32 enregistres
 */
async function loadDevices() {
    try {
        const response = await fetch('/api/esp32/devices');
        const data = await response.json();

        devicesContainer.innerHTML = '';

        if (data.devices && data.devices.length > 0) {
            data.devices.forEach(device => {
                const card = createDeviceCard(device);
                devicesContainer.appendChild(card);
            });
        } else {
            devicesContainer.innerHTML = `
                <div class="no-devices">
                    <h3>Aucun ESP32 enregistre</h3>
                    <p>Les ESP32 apparaitront ici quand ils se connecteront.</p>
                    <p class="hint">Assurez-vous que vos ESP32 sont configures pour envoyer leur adresse MAC.</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Erreur chargement devices:', error);
        devicesContainer.innerHTML = `
            <div class="error-message">
                <p>Erreur de connexion au serveur</p>
            </div>
        `;
    }
}

/**
 * Cree une carte pour un ESP32
 */
function createDeviceCard(device) {
    const card = document.createElement('div');
    card.className = 'device-card';
    card.id = `device-${device.mac_address.replace(/:/g, '')}`;

    const statusClass = device.status || 'unknown';
    const statusText = device.status_text || 'Inconnu';
    const sensorNum = device.sensor_number || '';
    const deviceName = device.name || 'Non configure';

    card.innerHTML = `
        <div class="device-header">
            <span class="device-mac">${device.mac_address}</span>
            <span class="status-dot ${statusClass}"></span>
        </div>

        <div class="device-info">
            <p class="device-status">${statusText}</p>
            <p class="device-ip">IP: ${device.ip_address || 'Inconnue'}</p>
            <p class="device-name">${deviceName}</p>
        </div>

        <div class="device-config">
            <label>Numero de capteur:</label>
            <div class="config-row">
                <select id="sensor-select-${device.mac_address.replace(/:/g, '')}" class="sensor-select">
                    <option value="">-- Choisir --</option>
                    ${[1,2,3,4,5,6,7,8,9,10].map(n =>
                        `<option value="${n}" ${sensorNum == n ? 'selected' : ''}>Capteur ${n}</option>`
                    ).join('')}
                </select>
                <input type="text"
                       id="name-input-${device.mac_address.replace(/:/g, '')}"
                       placeholder="Nom (optionnel)"
                       value="${device.name || ''}"
                       class="name-input">
            </div>
            <button onclick="configureDevice('${device.mac_address}')" class="btn-configure">
                Configurer
            </button>
        </div>

        <div class="device-actions">
            <button onclick="deleteDevice('${device.mac_address}')" class="btn-delete">
                Supprimer
            </button>
        </div>
    `;

    return card;
}

/**
 * Configure un ESP32 avec le numero de capteur selectionne
 */
async function configureDevice(macAddress) {
    const macId = macAddress.replace(/:/g, '');
    const selectEl = document.getElementById(`sensor-select-${macId}`);
    const nameEl = document.getElementById(`name-input-${macId}`);

    const sensorNumber = selectEl.value;
    const name = nameEl.value;

    if (!sensorNumber) {
        alert('Veuillez choisir un numero de capteur');
        return;
    }

    try {
        const response = await fetch('/api/esp32/configure', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                mac_address: macAddress,
                sensor_number: parseInt(sensorNumber),
                name: name || `Capteur ${sensorNumber}`
            })
        });

        const data = await response.json();

        if (response.ok) {
            alert(`ESP32 configure comme Capteur ${sensorNumber}`);
            loadDevices();
        } else {
            alert('Erreur: ' + (data.error || 'Echec de la configuration'));
        }
    } catch (error) {
        console.error('Erreur configuration:', error);
        alert('Erreur de connexion au serveur');
    }
}

/**
 * Supprime un ESP32 de la base de donnees
 */
async function deleteDevice(macAddress) {
    if (!confirm(`Supprimer l'ESP32 ${macAddress} ?`)) {
        return;
    }

    try {
        const response = await fetch('/api/esp32/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mac_address: macAddress })
        });

        const data = await response.json();

        if (response.ok) {
            loadDevices();
        } else {
            alert('Erreur: ' + (data.error || 'Echec de la suppression'));
        }
    } catch (error) {
        console.error('Erreur suppression:', error);
        alert('Erreur de connexion au serveur');
    }
}

/**
 * Actualise la liste des appareils
 */
function refreshDevices() {
    loadDevices();
}

// Charger les appareils au demarrage
loadDevices();

// Actualiser toutes les 30 secondes
setInterval(loadDevices, 30000);
