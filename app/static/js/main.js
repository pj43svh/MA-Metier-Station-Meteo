// ==================== CONFIGURATION ====================
const API_BASE = '/api';
const REFRESH_INTERVAL = 10000; // 10 secondes

// ==================== ÉTAT DE L'APPLICATION ====================
let capteurs = [];
let refreshTimer = null;

// ==================== INITIALISATION ====================
document.addEventListener('DOMContentLoaded', () => {
    updateDateTime();
    setInterval(updateDateTime, 1000);

    refreshData();
    refreshTimer = setInterval(refreshData, REFRESH_INTERVAL);
});

// ==================== DATE & HEURE ====================
function updateDateTime() {
    const now = new Date();

    const timeEl = document.getElementById('current-time');
    const dateEl = document.getElementById('current-date');

    if (timeEl) {
        timeEl.textContent = now.toLocaleTimeString('fr-FR', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    if (dateEl) {
        dateEl.textContent = now.toLocaleDateString('fr-FR', {
            weekday: 'long',
            day: 'numeric',
            month: 'long',
            year: 'numeric'
        });
    }
}

// ==================== API CALLS ====================
async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erreur API');
        }

        return await response.json();
    } catch (error) {
        console.error('Erreur API:', error);
        throw error;
    }
}

// ==================== RAFRAÎCHISSEMENT DES DONNÉES ====================
async function refreshData() {
    try {
        updateStatus('loading');

        capteurs = await fetchAPI('/mesures/latest');
        renderCapteurs();

        updateStatus('online');
        updateLastUpdate();
    } catch (error) {
        console.error('Erreur lors du rafraîchissement:', error);
        updateStatus('offline');
    }
}

function updateStatus(status) {
    const indicator = document.getElementById('status-indicator');
    const text = document.getElementById('status-text');

    if (!indicator || !text) return;

    indicator.className = 'status-indicator';

    switch (status) {
        case 'online':
            indicator.classList.add('online');
            text.textContent = 'Connecté';
            break;
        case 'offline':
            indicator.classList.add('offline');
            text.textContent = 'Hors ligne';
            break;
        case 'loading':
            text.textContent = 'Mise à jour...';
            break;
    }
}

function updateLastUpdate() {
    const el = document.getElementById('last-update');
    if (el) {
        el.textContent = new Date().toLocaleTimeString('fr-FR');
    }
}

// ==================== RENDU DES CAPTEURS ====================
function renderCapteurs() {
    const grid = document.getElementById('sensors-grid');
    const emptyState = document.getElementById('empty-state');

    if (!grid) return;

    // Affiche l'état vide si aucun capteur
    if (capteurs.length === 0) {
        grid.style.display = 'none';
        if (emptyState) emptyState.style.display = 'block';
        return;
    }

    grid.style.display = 'grid';
    if (emptyState) emptyState.style.display = 'none';

    grid.innerHTML = capteurs.map(capteur => renderCapteurCard(capteur)).join('');
}

function renderCapteurCard(capteur) {
    const isOnline = isRecentlyActive(capteur.derniere_connexion);
    const statusClass = isOnline ? 'online' : 'offline';
    const statusText = isOnline ? 'En ligne' : 'Hors ligne';

    const mesures = capteur.mesures || {};

    return `
        <div class="sensor-card ${statusClass}" onclick="showCapteurDetails(${capteur.id})">
            <div class="sensor-header">
                <div>
                    <div class="sensor-name">${escapeHtml(capteur.nom)}</div>
                    <div class="sensor-location">${escapeHtml(capteur.localisation || 'Non défini')}</div>
                </div>
                <span class="sensor-status ${statusClass}">${statusText}</span>
            </div>
            <div class="sensor-measurements">
                ${renderMeasurement(mesures.temperature, 'Température', '🌡️', '°C')}
                ${renderMeasurement(mesures.humidite, 'Humidité', '💧', '%')}
                ${renderMeasurement(mesures.pression, 'Pression', '🌀', 'hPa')}
            </div>
        </div>
    `;
}

function renderMeasurement(data, label, icon, defaultUnit) {
    if (!data) {
        return `
            <div class="measurement">
                <div class="measurement-icon">${icon}</div>
                <div class="measurement-value">--</div>
                <div class="measurement-label">${label}</div>
            </div>
        `;
    }

    const value = formatValue(data.valeur, label);
    const unit = data.unite || defaultUnit;

    return `
        <div class="measurement">
            <div class="measurement-icon">${icon}</div>
            <div class="measurement-value">${value}<small>${unit}</small></div>
            <div class="measurement-label">${label}</div>
        </div>
    `;
}

function formatValue(value, type) {
    if (value === null || value === undefined) return '--';

    if (type === 'Température' || type === 'Humidité') {
        return value.toFixed(1);
    }

    return Math.round(value);
}

function isRecentlyActive(lastConnection) {
    if (!lastConnection) return false;

    const last = new Date(lastConnection);
    const now = new Date();
    const diffMinutes = (now - last) / 1000 / 60;

    return diffMinutes < 5; // Considéré en ligne si activité dans les 5 dernières minutes
}

// ==================== MODAL AJOUT CAPTEUR ====================
function openAddCapteurModal() {
    const modal = document.getElementById('add-capteur-modal');
    if (modal) {
        modal.classList.add('active');
    }
}

function closeAddCapteurModal() {
    const modal = document.getElementById('add-capteur-modal');
    const form = document.getElementById('add-capteur-form');

    if (modal) {
        modal.classList.remove('active');
    }

    if (form) {
        form.reset();
    }
}

async function addCapteur(event) {
    event.preventDefault();

    const form = event.target;
    const data = {
        esp_id: form.esp_id.value.trim(),
        nom: form.nom.value.trim(),
        localisation: form.localisation.value.trim()
    };

    try {
        await fetchAPI('/capteurs', {
            method: 'POST',
            body: JSON.stringify(data)
        });

        closeAddCapteurModal();
        refreshData();

        showNotification('Capteur ajouté avec succès', 'success');
    } catch (error) {
        showNotification(error.message || 'Erreur lors de l\'ajout', 'error');
    }
}

// ==================== MODAL DÉTAILS CAPTEUR ====================
function showCapteurDetails(capteurId) {
    const capteur = capteurs.find(c => c.id === capteurId);
    if (!capteur) return;

    document.getElementById('detail-capteur-nom').textContent = capteur.nom;
    document.getElementById('detail-esp-id').textContent = capteur.esp_id;
    document.getElementById('detail-localisation').textContent = capteur.localisation || 'Non défini';
    document.getElementById('detail-derniere-connexion').textContent =
        capteur.derniere_connexion
            ? new Date(capteur.derniere_connexion).toLocaleString('fr-FR')
            : 'Jamais';

    const deleteBtn = document.getElementById('delete-capteur-btn');
    deleteBtn.onclick = () => deleteCapteur(capteurId);

    const modal = document.getElementById('capteur-details-modal');
    if (modal) {
        modal.classList.add('active');
    }
}

function closeCapteurDetailsModal() {
    const modal = document.getElementById('capteur-details-modal');
    if (modal) {
        modal.classList.remove('active');
    }
}

async function deleteCapteur(capteurId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce capteur ?')) {
        return;
    }

    try {
        await fetchAPI(`/capteurs/${capteurId}`, {
            method: 'DELETE'
        });

        closeCapteurDetailsModal();
        refreshData();

        showNotification('Capteur supprimé', 'success');
    } catch (error) {
        showNotification(error.message || 'Erreur lors de la suppression', 'error');
    }
}

// ==================== NOTIFICATIONS ====================
function showNotification(message, type = 'info') {
    // Simple alert pour l'instant, peut être amélioré avec des toasts
    alert(message);
}

// ==================== UTILITAIRES ====================
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Fermeture des modals en cliquant à l'extérieur
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
    }
});

// Fermeture avec Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal.active').forEach(modal => {
            modal.classList.remove('active');
        });
    }
});
